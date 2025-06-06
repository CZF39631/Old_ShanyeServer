from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash, jsonify
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies, create_access_token, get_jwt_identity
from APP.数据库.用户管理 import 验证用户, 创建用户, 初始化用户表
from APP.工具.认证 import 创建用户令牌
import uuid
import json
import hashlib
from datetime import datetime
import logging
import sqlite3

# 创建用户蓝图
用户蓝图 = Blueprint('用户', __name__)

# 确保用户表初始化
try:
    初始化用户表()
    logging.info("用户蓝图初始化时已检查用户表结构")
except Exception as e:
    logging.error(f"用户蓝图初始化时检查用户表结构失败: {e}")


@用户蓝图.route('/api/login', methods=['POST'])
def 登录API():
    """API登录端点，接收登录请求"""
    数据 = request.get_json()

    if not 数据 or not 'username' in 数据 or not 'password_hash' in 数据:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400

    用户名 = 数据['username']

    # 确保传递的是MD5哈希
    密码哈希 = 数据['password_hash']
    if not is_md5_hash(密码哈希):
        return jsonify({'success': False, 'message': '密码格式错误，请使用MD5加密'}), 400

    # 使用加密密码验证
    验证开始时间 = datetime.now()
    验证结果 = 验证用户(用户名, 密码哈希)
    验证耗时 = (datetime.now() - 验证开始时间).total_seconds() * 1000  # 毫秒
    logging.info(f"用户 {用户名} 的哈希密码验证耗时: {验证耗时:.2f}ms")

    if 验证结果:
        # 创建JWT令牌
        访问令牌 = 创建用户令牌(用户名)

        response = jsonify({'success': True, 'redirect': 数据.get('next', '/')})
        set_access_cookies(response, 访问令牌)
        return response
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401


@用户蓝图.route('/登录', methods=['GET', 'POST'])
def 登录页面():
    """登录页面路由"""
    if request.method == 'POST':
        # 不再支持传统表单提交，应通过前端JavaScript使用加密API
        return jsonify({
            'success': False,
            'message': '不支持直接表单提交，请使用前端加密API'
        }), 400

    # 获取下一页参数
    下一页 = request.args.get('next', '')

    return render_template('登录.html', next=下一页)


@用户蓝图.route('/登出')
def 登出():
    """登出路由"""
    响应 = make_response(redirect(url_for('用户.登录页面')))
    unset_jwt_cookies(响应)
    return 响应


@用户蓝图.route('/api/user/current')
def 获取当前用户():
    """获取当前登录用户信息"""
    try:
        当前用户 = get_jwt_identity()
        if 当前用户:
            return jsonify({'logged_in': True, 'username': 当前用户})
        else:
            return jsonify({'logged_in': False})
    except:
        return jsonify({'logged_in': False})


@用户蓝图.route('/api/admin/add_user', methods=['POST'])
def 添加用户API():
    """只允许特定IP地址添加用户的API端点"""
    # 获取客户端IP地址
    client_ip = request.remote_addr

    # 允许本地测试
    允许的IP = ['192.168.0.133', '127.0.0.1', 'localhost']

    # 检查IP地址是否允许访问
    if client_ip not in 允许的IP and not client_ip.startswith('192.168.0.'):
        logging.warning(f"未授权IP {client_ip} 尝试访问添加用户API")
        return jsonify({'success': False, 'message': '未授权的访问'}), 403

    logging.info(f"IP {client_ip} 正在尝试添加用户")

    try:
        # 获取JSON数据
        数据 = request.get_json()

        if not 数据 or 'username' not in 数据 or 'password' not in 数据:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400

        用户名 = 数据['username']
        密码 = 数据['password']
        邮箱 = 数据.get('email')
        是否管理员 = 数据.get('is_admin', False)

        # 确保密码已经是MD5哈希处理
        if not is_md5_hash(密码):
            return jsonify({'success': False, 'message': '密码必须使用MD5加密传输'}), 400

        logging.info(f"正在创建用户: {用户名}, 邮箱: {邮箱}, 是否管理员: {是否管理员}")

        # 添加用户，密码已是MD5哈希
        成功 = 创建用户(用户名, 密码, 邮箱, 是否管理员)

        if 成功:
            logging.info(f"用户 {用户名} 创建成功")
            return jsonify({'success': True, 'message': f'用户 {用户名} 创建成功'}), 201
        else:
            logging.error(f"用户 {用户名} 创建失败")
            return jsonify({'success': False, 'message': '用户创建失败，可能用户名或邮箱已存在'}), 400

    except Exception as e:
        logging.error(f"添加用户过程中发生错误: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


# 辅助函数：检查字符串是否为MD5哈希
def is_md5_hash(s):
    """检查字符串是否符合MD5哈希格式（32位十六进制字符）"""
    import re
    return bool(re.match(r'^[a-f0-9]{32}$', s, re.IGNORECASE))

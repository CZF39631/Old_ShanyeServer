import sqlite3  # 导入SQLite数据库模块
from ..工具 import 权大师请求
from flask import Blueprint, request, jsonify  # 导入Flask框架相关模块
from ..日志.日志 import 记录日志  # 记录日志函数
from ..工具.数据库操作 import 商标数据库操作

# 创建一个Flask蓝图对象，用于组织相关的路由和视图函数
商标库蓝图 = Blueprint('商标库', __name__)
数据库 = 商标数据库操作()

@商标库蓝图.route('/商标库/api/v1/申请号查询', methods=['POST'])
def 申请号查询():
    try:
        data = request.get_json()
        申请号 = data.get('申请号', '').strip()
        当前页 = int(data.get('当前页', 1))
        每页数量 = int(data.get('每页数量', 10))

        记录日志('INFO', f"收到申请号查询请求: 申请号={申请号}, 当前页={当前页}, 每页数量={每页数量}")

        数据库 = 商标数据库操作()
        查询结果 = 数据库.根据申请号查询商标(申请号, 当前页, 每页数量)
        总结果数量 = len(查询结果)
        数据库.关闭连接()

        总页数 = (总结果数量 + 每页数量 - 1) // 每页数量
        记录日志('INFO', f"申请号查询成功: 查询结果数量={总结果数量}, 总页数={总页数}, 查询结果={查询结果}")

        return jsonify({
            "查询结果": 查询结果,
            "查询结果数量": 总结果数量,
            "当前页": 当前页,
            "总页数": 总页数
        }), 200
    except Exception as e:
        记录日志('ERROR', f"申请号查询失败: {e}")
        return jsonify({"状态": "失败", "信息": f"发生错误: {str(e)}"}), 500


@商标库蓝图.route('/商标库/api/v1/商标库查询', methods=['POST'])
def 商标查询():
    try:
        data = request.get_json()
        小类关键字 = data.get('小类关键字', '').strip()
        商标名 = data.get('商标名', '')
        当前页 = int(data.get('当前页', 1))
        每页数量 = int(data.get('每页数量', 10))

        记录日志('INFO',
                 f"收到商标库查询请求: 小类关键字={小类关键字}, 商标名={商标名}, 当前页={当前页}, 每页数量={每页数量}")

        数据库 = 商标数据库操作()
        查询结果 = 数据库.根据查询条件查询商标(小类关键字, 商标名, 当前页, 每页数量)
        总结果数量 = 数据库.获取总数(小类关键字, 商标名)
        数据库.关闭连接()

        总页数 = (总结果数量 + 每页数量 - 1) // 每页数量
        记录日志('INFO', f"商标库查询成功: 查询结果={总结果数量}, 总页数={总页数}")

        return jsonify({
            "查询结果": 查询结果,
            "查询结果数量": 总结果数量,
            "当前页": 当前页,
            "总页数": 总页数
        }), 200
    except Exception as e:
        记录日志('ERROR', f"商标库查询失败: {e}")
        return jsonify({"状态": "失败", "信息": f"发生错误: {str(e)}"}), 500


@商标库蓝图.route('/商标库/api/v1/商标库翻页', methods=['POST'])
def 商标翻页():
    try:
        数据 = request.get_json()
        小类关键字 = 数据.get('小类关键字', '').strip()
        商标名 = 数据.get('商标名', '').strip()
        当前页 = 数据.get('当前页', 1)

        记录日志('INFO', f"收到商标库翻页请求: 小类关键字={小类关键字}, 商标名={商标名}, 当前页={当前页}")

        return 查询结果(小类关键字, 商标名, 当前页)
    except Exception as e:
        记录日志('ERROR', f"商标库翻页失败: {e}")
        return jsonify({"状态": "失败", "信息": f"发生错误: {str(e)}"}), 500


def 查询结果(小类关键字='', 商标名='', 申请号='', 当前页=1):
    每页数量 = 10
    try:
        数据库 = 商标数据库操作()
        总结果数量 = 数据库.获取总数(小类关键字, 商标名)
        总页数 = (总结果数量 + 每页数量 - 1) // 每页数量

        if 申请号:
            查询结果 = 数据库.根据申请号查询商标(申请号, 当前页, 每页数量)
        else:
            查询结果 = 数据库.根据查询条件查询商标(小类关键字.strip(), 商标名.strip(), 当前页, 每页数量)

        数据库.关闭连接()
        记录日志('INFO', f"查询结果成功: 总结果数量={总结果数量}, 当前页={当前页}, 总页数={总页数}")

        return jsonify({
            "查询结果": 查询结果,
            "查询结果数量": 总结果数量,
            "当前页": 当前页,
            "总页数": 总页数
        })
    except Exception as e:
        记录日志('ERROR', f"查询结果失败: {e}")
        return jsonify({"状态": "失败", "信息": f"发生错误: {str(e)}"}), 500


@商标库蓝图.route('/商标库/api/v1/插入商标', methods=['POST'])
def 插入商标():
    try:
        申请号 = request.data.decode('utf-8').strip()
        用户名 = request.form.get('用户名', '').strip()  # 获取用户名

        if not 申请号:
            记录日志('WARNING', "接收到空的申请号请求")
            return jsonify({"状态": "失败", "信息": "申请号不能为空"}), 400

        记录日志('INFO', f"接收到的申请号: {申请号}")
        数据库 = 商标数据库操作()
        商标信息 = 权大师请求.查询关键词(申请号)

        if not 商标信息:
            记录日志('WARNING', f"申请号 {申请号} 未找到相关商标信息")
            return jsonify({"状态": "失败", "信息": "未找到相关商标信息"}), 404

        插入结果 = 数据库.插入商标(商标信息, 用户名)  # 传递用户名给插入函数

        if 插入结果:
            记录日志('INFO', f"申请号 {申请号} 的商标信息已成功插入")
            # 将用户名存储在cookie中，过期时间为永久
            response = jsonify({"状态": "成功", "信息": f"申请号 {申请号} 的商标信息已成功插入"})
            response.set_cookie('用户名', 用户名, max_age=None)  # 设置cookie过期时间为永久
            return response
        else:
            记录日志('INFO', f"申请号 {申请号} 已存在，跳过插入")
            return jsonify({"状态": "失败", "信息": f"申请号 {申请号} 已存在"}), 409
    except sqlite3.Error as db_error:
        记录日志('ERROR', f"数据库操作错误: {db_error}")
        return jsonify({"状态": "失败", "信息": f"数据库错误: {str(db_error)}"}), 500
    except Exception as e:
        记录日志('ERROR', f"处理申请号时发生错误: {e}")
        return jsonify({"状态": "失败", "信息": f"发生未知错误: {str(e)}"}), 500


@商标库蓝图.route('/商标库/api/v1/修改备案', methods=['POST'])
def 修改备案():
    try:
        # 获取前端传来的 JSON 数据
        数据库 = 商标数据库操作()
        data = request.get_json()
        申请号 = data.get('申请号')
        备案平台 = data.get('备案平台')

        # 校验商标ID格式，商标ID应该是类似于 'xxxxxx_21' 这种格式
        # if not 申请号 or not isinstance(申请号, str) or not 申请号.count('_') == 1:
        #     return jsonify({'状态': '失败', '信息': '商标ID格式不正确，应该为类似 xxxx_21 的格式'}), 400

        # 调用数据库更新函数
        数据库.更新备案平台(申请号, 备案平台)  # 假设我们更新的是整个备案平台字符串

        # 返回成功响应
        return jsonify({'状态': '成功', '信息': '备案平台修改成功'}), 200

    except Exception as e:
        # 捕获异常并返回错误信息
        return jsonify({'状态': '失败', '信息': f'修改失败: {str(e)}'}), 500





@商标库蓝图.route('/商标库/api/v1/更新商标信息', methods=['POST'])
def 更新商标信息():
    try:
        数据库 = 商标数据库操作()
        # 1. 获取请求参数：申请号
        请求数据 = request.get_json()
        申请号 = 请求数据.get('申请号')

        if not 申请号:
            return jsonify({"状态": "失败", "信息": "缺少申请号"}), 400

        商标信息 = 权大师请求.查询关键词(申请号)

        数据库.更新商标信息(商标信息)

        # 4. 返回成功响应
        return jsonify({"状态": "成功", "信息": "商标信息更新成功"}), 200

    except Exception as e:
        # 捕获所有异常并返回错误信息
        return jsonify({"状态": "失败", "信息": f"出现错误: {str(e)}"}), 500

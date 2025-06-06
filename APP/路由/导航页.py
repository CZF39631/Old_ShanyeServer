from flask import Blueprint, render_template
from APP.工具.认证 import 需要登录  # 导入登录检查装饰器
from flask_jwt_extended import get_jwt_identity  # 导入获取用户身份的函数

# 创建导航页蓝图
导航页蓝图 = Blueprint('导航页', __name__)


@导航页蓝图.route('/')
@需要登录  # 添加登录检查
def 导航页():
    """
    主页路由
    :return: 渲染 index.html 模板
    """
    当前用户 = get_jwt_identity()
    return render_template('index.html', get_jwt_identity=get_jwt_identity, 当前用户=当前用户)  # 渲染主页模板


# 添加链接库的路由
@导航页蓝图.route('/链接库')
@需要登录  # 添加登录检查
def 链接库():
    """
    链接库页面路由
    :return: 渲染 链接库.html 模板
    """
    当前用户 = get_jwt_identity()
    return render_template('链接库.html', get_jwt_identity=get_jwt_identity, 当前用户=当前用户)  # 渲染链接库页面模板


@导航页蓝图.route('/商标库')
@需要登录  # 添加登录检查
def 商标库():
    """
    商标库页面路由
    :return: 渲染 商标查询.html 模板
    """
    当前用户 = get_jwt_identity()
    return render_template('商标查询.html', get_jwt_identity=get_jwt_identity, 当前用户=当前用户)  # 渲染商标查询页面模板


@导航页蓝图.route('/产品库')
@需要登录  # 添加登录检查
def 产品库():
    """
    商标库页面路由
    :return: 渲染 商标查询.html 模板
    """
    当前用户 = get_jwt_identity()
    return render_template('产品库.html', get_jwt_identity=get_jwt_identity, 当前用户=当前用户)  # 渲染商标查询页面模板

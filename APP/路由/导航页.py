from flask import Blueprint, render_template

# 创建导航页蓝图
导航页蓝图 = Blueprint('导航页', __name__)


@导航页蓝图.route('/')
def 导航页():
    """
    主页路由
    :return: 渲染 index.html 模板
    """
    return render_template('index.html')  # 渲染主页模板


# 添加链接库的路由
@导航页蓝图.route('/链接库')
def 链接库():
    """
    链接库页面路由
    :return: 渲染 链接库.html 模板
    """
    return render_template('链接库.html')  # 渲染链接库页面模板


@导航页蓝图.route('/商标库')
def 商标库():
    """
    商标库页面路由
    :return: 渲染 商标查询.html 模板
    """
    return render_template('商标查询.html')  # 渲染商标查询页面模板


@导航页蓝图.route('/产品库')
def 产品库():
    """
    商标库页面路由
    :return: 渲染 商标查询.html 模板
    """
    return render_template('产品库.html')  # 渲染商标查询页面模板

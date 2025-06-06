import logging
from flask import Flask
from APP.路由.导航页 import 导航页蓝图
from APP.路由.链接库 import 链接库蓝图  # 导入定时任务启动方法
from APP.路由.商标库 import 商标库蓝图
from APP.路由.用户 import 用户蓝图  # 导入用户蓝图
from APP.日志.日志 import 配置日志  # 引入日志工具
from APP.工具.链接库定时清除 import 启动定时任务
from APP.工具.认证 import 配置JWT  # 导入JWT配置工具
from APP.数据库.用户管理 import 初始化用户表  # 导入用户表初始化
from config import 调试模式, 服务端口  # 导入配置


def create_app():
    # 创建 Flask 应用
    app = Flask(__name__)

    # 注册蓝图
    app.register_blueprint(导航页蓝图)
    app.register_blueprint(链接库蓝图)
    app.register_blueprint(商标库蓝图)
    app.register_blueprint(用户蓝图)  # 注册用户蓝图

    # 配置密钥
    app.config['SECRET_KEY'] = 'your-secret-key'  # 在生产环境中应使用安全的密钥
    
    # 配置JWT
    配置JWT(app)
    
    # 启动定时任务
    启动定时任务()
    
    # 初始化用户表
    try:
        logging.info("正在初始化用户表...")
        初始化用户表()
        logging.info("用户表初始化完成")
    except Exception as e:
        logging.error(f"初始化用户表时发生错误: {e}")

    return app


if __name__ == '__main__':
    # 配置日志
    配置日志()  # 调用日志工具配置日志
    # 创建应用
    app = create_app()

    # 记录启动信息
    logging.info(f"Flask 应用已启动，正在监听端口 {服务端口}...")

    # 启用多线程支持
    app.run(host='0.0.0.0', port=服务端口, debug=调试模式, threaded=True)

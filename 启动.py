
import logging
from flask import Flask
from APP.路由.导航页 import 导航页蓝图
from APP.路由.链接库 import 链接库蓝图  # 导入定时任务启动方法
from APP.路由.商标库 import 商标库蓝图
from APP.路由.产品库 import 产品库蓝图
from APP.日志.日志 import 配置日志  # 引入日志工具
from APP.工具.链接库定时清除 import 启动定时任务


def create_app():
    # 创建 Flask 应用
    app = Flask(__name__)

    # 注册蓝图
    app.register_blueprint(导航页蓝图)
    app.register_blueprint(链接库蓝图)
    app.register_blueprint(商标库蓝图)
    app.register_blueprint(产品库蓝图)

    # 启动定时任务
    启动定时任务()

    return app


if __name__ == '__main__':
    # 配置日志
    配置日志()  # 调用日志工具配置日志

    # 创建应用
    app = create_app()

    # 记录启动信息
    logging.info("Flask 应用已启动，正在监听端口 8087...")


    # 启用多线程支持
    app.run(host='0.0.0.0', port=8087, debug=True, threaded=True)

# config.py
import os

# 从环境变量中获取配置，如果没有则使用默认值
定时删除范围 = os.environ.get('定时删除范围', '30')  # 默认30天
数据库 = os.environ.get('数据库路径', 'APP/数据库/综合库2.db')  # 数据库路径
# 调试模式 = os.environ.get('调试模式', 'False').lower() == 'true'  # 默认关闭调试模式
服务端口 = int(os.environ.get('服务端口', '8084'))  # 默认端口8087
调试模式 = True

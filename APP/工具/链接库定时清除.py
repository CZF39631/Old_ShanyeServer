import threading
import time
from datetime import datetime, timedelta
import config
import schedule

from ..工具.数据库操作 import 链接库数据库操作
from ..日志.日志 import 记录日志  # 记录日志函数

# 定时清除过期数据
from datetime import datetime, timedelta


def 清除过期数据():
    当前时间 = datetime.now()
    记录日志("INFO", f"开始清除过期数据，当前时间: {当前时间}")

    目标客户 = ['小米']
    白名单日期 = '2024-01-01'

    数据库 = 链接库数据库操作()

    # 获取定时删除范围（过期天数）
    过期天数 = config.定时删除范围

    # 计算删除日期
    删除日期 = 当前时间 - timedelta(days=int(过期天数))

    # 转换为字符串格式（YYYY-MM-DD）
    删除日期字符串 = 删除日期.strftime('%Y-%m-%d')

    print(f"计算出来的删除日期: {删除日期字符串}")

    # 调用数据库操作函数执行删除，传入删除日期和目标客户
    删除信息 = 数据库.通过日期删除并排除白名单(删除日期字符串, 目标客户, 白名单日期)
    print(f"删除记录数: {删除信息}")
    数据库.关闭连接()

    记录日志("INFO", f"清除过期数据完成，删除记录数: {删除信息}")


def 定时任务线程():
    schedule.every().day.at("23:00:00").do(清除过期数据)

    while True:
        schedule.run_pending()
        time.sleep(1)


def 启动定时任务():
    记录日志("INFO", "启动定时任务线程")
    线程 = threading.Thread(target=定时任务线程, daemon=True)
    线程.start()



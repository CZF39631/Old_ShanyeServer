from APP.工具.数据库操作 import 链接库数据库操作
from APP.工具.链接库定时清除 import 清除过期数据

数据库 = 链接库数据库操作()
if __name__ == '__main__':
    清除过期数据()


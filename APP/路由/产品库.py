import sqlite3
from flask import Blueprint, request, jsonify
from ..日志.日志 import 记录日志

# 创建一个蓝图用于处理产品相关路由
产品库蓝图 = Blueprint('产品库', __name__)

class 产品数据库操作:
    def __init__(self, 数据库文件='数据库/产品库.db'):
        self.连接 = None
        self.游标 = None
        try:
            self.连接 = sqlite3.connect(数据库文件)
            self.游标 = self.连接.cursor()
            记录日志('INFO', f"成功连接到数据库: {数据库文件}")
        except sqlite3.Error as e:
            记录日志('ERROR', f"数据库连接错误: {e}")

    def 获取总数(self, 品类='', 品名=''):
        try:
            sql = "SELECT COUNT(*) FROM 产品库"
            params = []
            where_clauses = []

            if 品类:
                where_clauses.append("品类 LIKE ?")
                params.append(f'%{品类}%')  # 模糊匹配

            if 品名:
                where_clauses.append("品名 LIKE ?")
                params.append(f'%{品名}%')  # 模糊匹配

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            记录日志('INFO', f"执行获取总数查询: {sql}，参数: {params}")
            self.游标.execute(sql, params)
            return self.游标.fetchone()[0]
        except sqlite3.Error as e:
            记录日志('ERROR', f"查询总数错误: {e}")
            return 0

    def 根据查询条件查询产品(self, 品类='', 品名='', 当前页=1, 每页数量=30):
        try:
            sql = "SELECT 品类, 品名, 产品型号, 产品图片, 产品链接 FROM 产品库"
            params = []
            where_clauses = []

            if 品类:
                where_clauses.append("品类 LIKE ?")
                params.append(f'%{品类}%')

            if 品名:
                where_clauses.append("品名 LIKE ?")
                params.append(f'%{品名}%')

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            sql += " LIMIT ? OFFSET ?"
            params.extend([每页数量, (当前页 - 1) * 每页数量])

            记录日志('INFO', f"执行产品查询: {sql}，参数: {params}")
            self.游标.execute(sql, params)
            return self.游标.fetchall()
        except sqlite3.Error as e:
            记录日志('ERROR', f"查询错误: {e}")
            return []

    def 关闭连接(self):
        if self.连接:
            self.连接.close()
            记录日志('INFO', "数据库连接已关闭")


@产品库蓝图.route('/产品库查询', methods=['POST'])
def 产品查询():
    try:
        data = request.get_json()
        品类 = data.get('品类', '')  # 获取品类
        品名 = data.get('品名', '')  # 获取品名
        当前页 = int(data.get('当前页', 1))
        每页数量 = int(data.get('每页数量', 10))

        记录日志('INFO', f"收到产品库查询请求: 品类={品类}, 品名={品名}, 当前页={当前页}, 每页数量={每页数量}")

        数据库 = 产品数据库操作()
        查询结果 = 数据库.根据查询条件查询产品(品类, 品名, 当前页, 每页数量)
        总结果数量 = 数据库.获取总数(品类, 品名)
        数据库.关闭连接()

        记录日志('INFO', f"查询成功: 查询结果数量={总结果数量}")
        return jsonify({
            "查询结果": 查询结果,
            "查询结果数量": 总结果数量,
            "当前页": 当前页,
            "总页数": (总结果数量 + 每页数量 - 1) // 每页数量  # 计算总页数
        })
    except Exception as e:
        记录日志('ERROR', f"产品查询时发生错误: {e}")
        return jsonify({"错误": "查询失败"}), 500


# 路由：产品翻页
@产品库蓝图.route('/产品库翻页', methods=['POST'])
def 产品翻页():
    try:
        数据 = request.get_json()
        品类 = 数据.get('品类', '')  # 获取品类
        品名 = 数据.get('品名', '')  # 获取品名
        当前页 = int(数据.get('当前页', 1))

        记录日志('INFO', f"收到产品库翻页请求: 品类={品类}, 品名={品名}, 当前页={当前页}")
        return 产品查询()
    except Exception as e:
        记录日志('ERROR', f"产品翻页时发生错误: {e}")
        return jsonify({"错误": "翻页失败"}), 500

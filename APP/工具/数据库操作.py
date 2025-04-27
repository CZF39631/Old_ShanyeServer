#!/user/bin/env python3
# -*- coding: utf-8 -*-
import math
import os
import re
import sqlite3
from datetime import datetime

import pandas as pd

import config
from ..日志.日志 import 记录日志  # 假设有一个日志模块和记录日志函数

数据库 = config.数据库


def 数据库链接():
    绝对路径 = os.path.abspath(数据库)
    print(f"数据库全路径: {绝对路径}")  # 打印数据库绝对路径
    数据库链接 = sqlite3.connect(绝对路径)
    return 数据库链接


# 测试连接
数据库链接()


class 链接库数据库操作:
    def __init__(self):
        self.连接 = 数据库链接()
        self.游标 = self.连接.cursor()
        self.创建表()

    def 创建表(self):
        self.游标.execute('''  
        CREATE TABLE IF NOT EXISTS 链接库 (
            序号 INTEGER PRIMARY KEY AUTOINCREMENT,
            客户名 TEXT ,
            平台 TEXT ,
            店铺名字 TEXT,
            掌柜ID TEXT,
            链接ID TEXT NOT NULL UNIQUE,
            类别 TEXT NOT NULL,
            检索日期 DATETIME,
            检索周期 TEXT,
            IS_Delete integer NOT NULL ,
            Date_Delete DATETIME
        )
        ''')
        self.连接.commit()

    import math

    def 查询数据(self, 文件路径):
        查询结果 = []
        数据框字典 = pd.read_excel(文件路径, sheet_name=None, dtype=str)  # 读取所有 sheet
        链接ID列表 = []

        # 收集所有 sheet 中的链接 ID
        for sheet_name, 数据框 in 数据框字典.items():
            if '链接ID' in 数据框.columns:
                print(f"Sheet '{sheet_name}' 存在 '链接ID' 列")
                链接ID列表.extend(数据框['链接ID'].tolist())
            else:
                print(f"Sheet '{sheet_name}' 中 '链接ID' 列未检测到，请检查文件")

        # 获取数据库表的列名
        self.游标.execute("PRAGMA table_info(链接库)")  # 获取表结构信息
        表结构 = self.游标.fetchall()

        # 找到 Delete 和 类别 字段的索引
        delete索引 = next((i for i, col in enumerate(表结构) if col[1] == "Is_Delete"), None)
        类别索引 = next((i for i, col in enumerate(表结构) if col[1] == "类别"), None)

        if delete索引 is None:
            raise ValueError("数据库表 '链接库' 中未找到 'Is_Delete' 字段")

        if 类别索引 is None:
            raise ValueError("数据库表 '链接库' 中未找到 '类别' 字段")

        # 查询数据库中的记录，确保与上传文件的链接ID一一对应
        for 链接ID in 链接ID列表:
            self.游标.execute('''SELECT * FROM 链接库 WHERE 链接ID = ?''', (链接ID,))
            记录 = self.游标.fetchone()

            if 记录:
                delete字段 = 记录[delete索引]  # 获取 Delete 字段的值
                if delete字段 == 1:
                    # Delete = 1，表示该数据被删除，认定为未记录
                    查询结果.append((str(链接ID), "未记录ID"))
                else:
                    # Delete = 0 或 None 或 空字符串，表示数据存在，输出类别字段
                    类别字段 = 记录[类别索引]

                    # 清洗类别字段，确保可序列化
                    if 类别字段 is None or (isinstance(类别字段, float) and math.isnan(类别字段)):
                        类别字段 = "未知类别"

                    查询结果.append((str(链接ID), str(类别字段)))
            else:
                # 数据库没有查到，认定为未记录ID
                查询结果.append((str(链接ID), "未记录ID"))

        # 检查查询结果是否为空
        if not 查询结果:
            print("查询结果为空，可能没有匹配的数据")
            return []

        # 确保查询结果格式正确
        for item in 查询结果:
            if not isinstance(item, tuple) or len(item) != 2:
                print(f"查询结果格式错误: {item}")
                return []

        return 查询结果

    def 上传数据(self, 文件路径):
        # 从文件名中提取客户名
        文件名 = os.path.basename(文件路径)
        客户名匹配 = re.match(r"^(.*?)[-_+].*链接库", 文件名)
        客户名 = 客户名匹配.group(1) if 客户名匹配 else "未知客户"

        数据框字典 = pd.read_excel(文件路径, sheet_name=None)  # 读取所有 sheet
        上传成功的数量 = 0
        上传失败的记录 = []

        for sheet_name, 数据框 in 数据框字典.items():
            for _, 行 in 数据框.iterrows():
                # 检查链接ID是否为空
                if pd.isnull(行['链接ID']):
                    print(f"跳过空链接ID记录: {行}")
                    continue

                try:
                    链接ID = str(行['链接ID']).strip()
                    类别 = 行.get('类别（侵权/不侵权）', "").strip()  # 获取类别字段

                    # 检查类别是否为空
                    if not 类别:
                        raise ValueError("类别字段不能为空")

                    # 查询数据库是否存在该链接ID，并获取 Is_Delete 和 Date_Delete
                    self.游标.execute('SELECT Is_Delete FROM 链接库 WHERE 链接ID = ?', (链接ID,))
                    记录 = self.游标.fetchone()

                    if 记录:
                        is_delete = 记录[0]
                        if is_delete == 1:
                            # **恢复数据**
                            self.游标.execute('''
                            UPDATE 链接库 
                            SET 客户名 = ?, 平台 = ?, 店铺名字 = ?, 掌柜ID = ?, 类别 = ?, 检索日期 = ?, 检索周期 = ?, 
                                Is_Delete = 0, Date_Delete = NULL
                            WHERE 链接ID = ?
                            ''', (
                                客户名,
                                sheet_name,
                                行.get('店铺名字（有可填写）', None),
                                行.get('掌柜ID（有可填写）', None),
                                类别,
                                行.get('检索日期', None),
                                行.get('检索周期', None),
                                链接ID
                            ))
                            上传成功的数量 += 1  # 计入成功
                        else:
                            # **数据存在但未删除，跳过**
                            记录日志('Error', f"链接ID {链接ID} 已存在且未删除，跳过上传")
                            continue
                    else:
                        # **插入新数据**
                        self.游标.execute(''' 
                        INSERT INTO 链接库 (客户名, 平台, 店铺名字, 掌柜ID, 链接ID, 类别, 检索日期, 检索周期, Is_Delete, Date_Delete) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                        ''', (
                            客户名,
                            sheet_name,
                            行.get('店铺名字（有可填写）', None),
                            行.get('掌柜ID（有可填写）', None),
                            链接ID,
                            类别,
                            行.get('检索日期', None),
                            行.get('检索周期', None),
                            0  # 明确指定 Is_Delete 为 0
                        ))
                        上传成功的数量 += 1  # 计入成功

                except Exception as e:
                    上传失败的记录.append({
                        "客户名": 客户名,
                        "平台": sheet_name,
                        "店铺名字": 行.get('店铺名字（有可填写）', None),
                        "掌柜ID": 行.get('掌柜ID（有可填写）', None),
                        "链接ID": str(链接ID),
                        "类别": 类别,
                        "检索日期": 行.get('检索日期', None),
                        "检索周期": 行.get('检索周期', None),
                        "错误信息": str(e),  # 记录错误信息
                        "Is_Delete": 0  # 保持一致
                    })

        self.连接.commit()

        return 上传成功的数量, 上传失败的记录

    def 处理查询功能(self, 文件路径):
        查询结果 = self.查询数据(文件路径)

        # 只保留链接ID和侵权情况两列
        结果数据框 = pd.DataFrame(查询结果, columns=["链接ID", "侵权情况"])

        结果文件路径 = "查询结果.xlsx"
        结果数据框.to_excel(结果文件路径, index=False)

        return 查询结果, 结果文件路径

    def 根据链接ID查询客户名(self, 链接ID):
        self.游标.execute("SELECT 客户名, 类别 FROM 链接库 WHERE 链接ID=?", (链接ID,))
        result = self.游标.fetchone()

        if result:
            return {
                "客户名": result[0],  # 返回客户名
                "类别": result[1]  # 返回类别
            }
        return None

    def 通过日期删除并排除白名单(self, 删除日期, 目标客户列表, 白名单日期):
        """
        通过删除日期来删除记录，并排除白名单日期的记录
        :param 删除日期: 删除的日期（格式: 'YYYY-MM-DD'）
        :param 目标客户列表: 需要删除的客户列表（例如: ['小米', '方太']）
        :param 白名单日期: 白名单日期，排除此日期的记录（格式: 'YYYY-MM-DD'）
        """
        if not 目标客户列表:
            记录日志("ERROR", "目标客户列表为空")
            return 0  # 返回0表示没有删除记录

        try:
            # 连接到数据库
            with self.连接 as conn:
                cursor = conn.cursor()

                # 构建SQL查询语句
                query = """
                UPDATE "链接库"
                SET 
                  "Is_Delete" = 1,
                  "Date_Delete" = strftime('%s', 'now')
                WHERE 
                  "客户名" IN ({})
                  AND "Is_Delete" = 0
                  AND strftime('%Y-%m-%d', REPLACE("检索日期", '.', '-')) <= ?
                  AND strftime('%Y-%m-%d', REPLACE("检索日期", '.', '-')) <> ?
                """.format(','.join(['?'] * len(目标客户列表)))

                # 执行SQL语句
                cursor.execute(query, (*目标客户列表, 删除日期, 白名单日期))

                # 提交更改
                conn.commit()

                # 返回删除的记录数
                记录日志('info', f"成功更新 {cursor.rowcount} 条记录")
                return cursor.rowcount  # 返回删除的记录数

        except sqlite3.Error as e:
            记录日志('error', f"数据库操作失败: {e}")
            return 0  # 发生错误时返回0
        except Exception as e:
            记录日志('error', f"发生错误: {e}")
            return 0  # 发生错误时返回0

    def 关闭连接(self):
        """关闭数据库连接"""
        self.连接.close()


class 商标数据库操作:
    def __init__(self):
        self.连接 = None
        self.游标 = None
        try:
            self.连接 = 数据库链接()
            self.游标 = self.连接.cursor()
        except sqlite3.Error as e:
            记录日志('ERROR', f"数据库连接错误: {e}")

    def 获取总数(self, 小类关键字='', 商标名=''):
        try:
            sql = "SELECT COUNT(*) FROM 小米商标库"
            params = []
            where_clauses = []

            if 小类关键字:
                where_clauses.append("未删除小类 LIKE ?")
                params.append(f'%{小类关键字}%')

            if 商标名:
                where_clauses.append("商标名 = ?")
                params.append(商标名)

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            记录日志('INFO', f"执行获取总数查询: {sql}，参数: {params}")
            self.游标.execute(sql, params)
            return self.游标.fetchone()[0]
        except sqlite3.Error as e:
            记录日志('ERROR', f"查询总数错误: {e}")
            return 0

    def 根据查询条件查询商标(self, 小类关键字, 商标名, 当前页, 每页数量):
        try:
            sql = "SELECT 商标图链接, 商标名, 申请人, 申请号, 未删除小类, 备案平台,提交时间 FROM 小米商标库"
            params = []
            where_clauses = []

            if 小类关键字:
                where_clauses.append("未删除小类 LIKE ?")
                params.append(f'%{小类关键字}%')

            if 商标名:
                where_clauses.append("商标名 = ?")
                params.append(商标名)

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            sql += " LIMIT ? OFFSET ?"
            params.extend([每页数量, (当前页 - 1) * 每页数量])

            记录日志('INFO', f"执行商标查询: {sql}，参数: {params}")
            self.游标.execute(sql, params)
            return self.游标.fetchall()
        except sqlite3.Error as e:
            记录日志('ERROR', f"查询错误: {e}")
            return []

    def 根据申请号查询商标(self, 申请号, 当前页, 每页数量):
        try:
            sql = "SELECT 商标图链接, 商标名, 申请人, 申请号, 未删除小类, 备案平台,提交时间 FROM 小米商标库 WHERE 申请号 LIKE ? LIMIT ? OFFSET ?"
            params = [申请号 + "%", 每页数量, (当前页 - 1) * 每页数量]

            记录日志('INFO', f"执行申请号查询: {sql}，参数: {params}")
            self.游标.execute(sql, params)
            return self.游标.fetchall()
        except sqlite3.Error as e:
            记录日志('ERROR', f"申请号查询错误: {e}")
            return []

    def 关闭连接(self):
        if self.连接:
            self.连接.close()
            记录日志('INFO', "数据库连接已关闭")

    def 插入商标(self, 商标数据, 用户名):
        try:
            检查_sql = "SELECT COUNT(*) FROM 小米商标库 WHERE 申请号 = ?"
            self.游标.execute(检查_sql, (商标数据.get('申请号', ''),))
            结果 = self.游标.fetchone()
            当前时间 = datetime.now().strftime('%Y-%m-%d')

            if 结果 and 结果[0] > 0:
                记录日志('INFO', f"申请号 {商标数据.get('申请号')} 已存在，跳过插入")
                return False

            插入_sql = """
                INSERT INTO 小米商标库 (商标图链接, 商标名, 申请人, 申请号, 未删除小类, 备案平台,提交人,提交时间)
                VALUES (?, ?, ?, ?, ?, ?,?,?)
            """
            self.游标.execute(插入_sql, (
                商标数据.get('商标图链接', ''),
                商标数据.get('商标名', ''),
                商标数据.get('申请人', ''),
                商标数据.get('申请号', ''),
                商标数据.get('未删除小类', ''),
                商标数据.get('备案平台', ''),
                用户名,
                当前时间
            ))
            self.连接.commit()
            记录日志('INFO', f"成功插入商标数据: {商标数据}")
            return True
        except sqlite3.Error as e:
            记录日志('ERROR', f"插入商标错误: {e}")
            return False

    def 更新备案平台(self, 申请号, 新备案平台):
        try:
            # 更新备案平台的 SQL 语句
            sql = "UPDATE 小米商标库 SET 备案平台 = ? WHERE 申请号 LIKE ?"
            params = [新备案平台, 申请号]

            记录日志('INFO', f"执行更新备案平台: {sql}，参数: {params}")

            # 执行 SQL 更新操作
            self.游标.execute(sql, params)
            self.连接.commit()  # 提交事务

            记录日志('INFO', f"申请号 {申请号} 的备案平台已更新为 {新备案平台}")
            return True  # 更新成功
        except sqlite3.Error as e:
            记录日志('ERROR', f"更新备案平台失败: {e}")
            return False  # 更新失败

    def 更新商标信息(self, 商标数据):
        用户名 = '系统'  # 因为数据从平台接口获取，所以使用系统作为用户名
        try:
            # 检查商标是否存在
            检查_sql = "SELECT COUNT(*) FROM 小米商标库 WHERE 申请号 = ?"
            self.游标.execute(检查_sql, (商标数据.get('申请号', ''),))
            结果 = self.游标.fetchone()

            if not 结果 or 结果[0] == 0:
                记录日志('INFO', f"申请号 {商标数据.get('申请号')} 不存在，无法更新")
                return False

            # 获取当前时间戳
            当前时间戳 = int(datetime.now().timestamp())

            # 只更新需要修改的字段，不包括备案平台
            更新_sql = """
                UPDATE 小米商标库
                SET 商标图链接 = ?, 商标名 = ?, 申请人 = ?, 未删除小类 = ?, 提交人 = ?, 提交时间 = ?
                WHERE 申请号 = ?
            """
            self.游标.execute(更新_sql, (
                商标数据.get('商标图链接', ''),  # 商标图链接
                商标数据.get('商标名', ''),  # 商标名
                商标数据.get('申请人', ''),  # 申请人
                商标数据.get('未删除小类', ''),  # 未删除小类
                用户名,  # 提交人
                当前时间戳,  # 提交时间
                商标数据.get('申请号', '')  # 申请号
            ))
            self.连接.commit()
            记录日志('INFO', f"成功更新商标数据: {商标数据}")
            return True

        except sqlite3.Error as e:
            记录日志('ERROR', f"更新商标错误: {e}")
            return False

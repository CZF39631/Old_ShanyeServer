import os
from datetime import datetime

from flask import Blueprint, request, jsonify, render_template

from ..工具.数据库操作 import 链接库数据库操作
from ..日志.日志 import 记录日志  # 记录日志函数

链接库蓝图 = Blueprint('链接库', __name__)


# 显示链接库页面
@链接库蓝图.route('/链接库', methods=['GET'])
def 链接库页面():
    记录日志("INFO", "访问链接库页面")
    return render_template('链接库.html')


# 上传链接库数据
@链接库蓝图.route('/链接库/api/v1/上传', methods=['POST'])
def 链接库上传():
    if 'file' not in request.files:
        记录日志("WARNING", "上传链接库数据时未提供文件")
        return jsonify({"message": "没有文件上传"}), 400

    file = request.files['file']
    if file.filename == '':
        记录日志("WARNING", "上传链接库数据时未选择文件")
        return jsonify({"message": "没有选择文件"}), 400

    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    记录日志("INFO", f"文件已保存到 {file_path}")

    数据库 = 链接库数据库操作()
    上传成功数量, 上传失败记录 = 数据库.上传数据(file_path)
    数据库.关闭连接()

    上传时间 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    记录日志("INFO", f"文件 {file.filename} 上传成功，插入记录 {上传成功数量} 条")

    return jsonify({
        "message": f"文件 {file.filename} 上传成功，成功插入 {上传成功数量} 条记录！",
        "upload_time": 上传时间,
        "success_count": 上传成功数量,
        "failed_records": 上传失败记录
    })


# 查询链接库数据
@链接库蓝图.route('/链接库/api/v1/查询', methods=['POST'])
def 链接库查询():
    if 'file' not in request.files:
        记录日志("WARNING", "查询链接库数据时未提供文件")
        return jsonify({"message": "没有文件上传"}), 400

    file = request.files['file']
    if file.filename == '':
        记录日志("WARNING", "查询链接库数据时未选择文件")
        return jsonify({"message": "没有选择文件"}), 400

    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    记录日志("INFO", f"查询文件已保存到 {file_path}")

    数据库 = 链接库数据库操作()
    查询结果, 结果文件路径 = 数据库.处理查询功能(file_path)
    数据库.关闭连接()

    查询时间 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    记录日志("INFO", f"查询成功，结果记录数: {len(查询结果)}")

    return jsonify({
        "message": "查询成功！",
        "query_time": 查询时间,
        "data_count": len(查询结果),
        "data": 查询结果
    })


@链接库蓝图.route('/链接库/api/v1/ID查询', methods=['POST'])
def 链接ID查询():
    data = request.get_json()
    link_id = data.get('link_id')

    if not link_id:
        记录日志("WARNING", "链接ID查询时未提供链接ID")
        return jsonify({"message": "链接ID不能为空"}), 400

    数据库 = 链接库数据库操作()
    查询结果 = 数据库.根据链接ID查询客户名(link_id)
    数据库.关闭连接()

    if 查询结果:
        记录日志("INFO", f"链接ID {link_id} 查询成功")
        return jsonify({
            "customer_name": 查询结果["客户名"],
            "类别": 查询结果["类别"]
        })
    else:
        记录日志("INFO", f"链接ID {link_id} 未找到相关记录")
        return jsonify({"message": "找不到链接记录"}), 404

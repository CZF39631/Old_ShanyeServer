# 使用 Python 基础镜像
FROM hub.1panel.dev/library/python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口
EXPOSE 8084

# 启动命令
CMD ["python", "启动.py"]
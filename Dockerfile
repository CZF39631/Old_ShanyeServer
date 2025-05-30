# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置国内的 Debian 软件包源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 更新系统软件包并安装必要的依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 创建.pip 目录并配置 pip 源为阿里云镜像
RUN mkdir ~/.pip
COPY pip.conf ~/.pip/pip.conf

# 复制项目依赖文件到工作目录
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目到工作目录
COPY . .

# 暴露应用运行的端口
EXPOSE 8087

# 设置环境变量，可根据需要调整
ENV FLASK_APP=启动.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8087

# 运行应用
CMD ["flask", "run"]
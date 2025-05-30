FROM python:3.10-slim

# 设置环境变量（避免中文乱码、禁用 Python 缓冲）
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

# 创建工作目录并设置权限
WORKDIR /app
RUN chown -R 1000:1000 /app

# 替换为阿里源并更新（不安装 PostgreSQL）
RUN echo "deb http://mirrors.aliyun.com/debian bookworm main contrib non-free\n\
deb http://mirrors.aliyun.com/debian bookworm-updates main contrib non-free\n\
deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8087

# 启动应用（注意检查“启动.py”和 create_app 函数是否存在）
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8087", "启动:create_app()", "--access-logfile", "-", "--error-logfile", "-"]

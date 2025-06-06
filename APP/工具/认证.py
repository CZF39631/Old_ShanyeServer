from functools import wraps
from flask import request, redirect, url_for, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token, JWTManager
import os
from datetime import timedelta

# 初始化JWT管理器
jwt = JWTManager()

def 配置JWT(app):
    """配置JWT管理器"""
    # 从环境变量获取密钥，如果没有则使用默认值
    jwt_secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
    
    app.config['JWT_SECRET_KEY'] = jwt_secret_key
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False  # 在生产环境中应设为True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)  # 7天
    jwt.init_app(app)

def 需要登录(f):
    """检查用户是否已登录的装饰器"""
    @wraps(f)
    def 装饰函数(*args, **kwargs):
        try:
            verify_jwt_in_request()
            # 获取当前用户身份
            当前用户 = get_jwt_identity()
            if not 当前用户:
                return redirect(url_for('用户.登录页面', next=request.path))
            return f(*args, **kwargs)
        except Exception as e:
            print(f"登录验证错误: {e}")
            return redirect(url_for('用户.登录页面', next=request.path))
    return 装饰函数

def 创建用户令牌(用户名):
    """为用户创建JWT令牌"""
    # 使用用户名作为字符串身份标识
    access_token = create_access_token(identity=用户名)
    return access_token 
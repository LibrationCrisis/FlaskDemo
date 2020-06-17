from functools import wraps
from flask import session, redirect, url_for


# 登录限制装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 判断是否已登录
        if session.get("user_id"):
            return func(*args, **kwargs)
        else:
            # 跳转登录页面
            return redirect(url_for("login"))

    return wrapper

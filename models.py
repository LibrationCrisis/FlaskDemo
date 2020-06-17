# encoding:UTF-8

from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # 加密密码过滤
    def __init__(self, *args, **kwargs):
        email = kwargs.get("email")
        username = kwargs.get("username")
        password = kwargs.get("password")

        self.email = email
        self.username = username
        self.password = generate_password_hash(password)

    # 密码检查
    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # now() 获取的是服务器第一次运行的时间
    # now 每次创建model时都获取当前时间
    create_time = db.Column(db.DateTime, default=datetime.now)

    # 外键关系
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # 模型对象
    author = db.relationship("User", backref=db.backref("questions"))


class Answer(db.Model):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    question = db.relationship("Question", backref=db.backref("answers", order_by=create_time.desc()))
    author = db.relationship("User", backref=db.backref("answers"))

from flask import Flask, render_template, request, redirect, url_for, session, g
from sqlalchemy import or_

import config
from decorators import login_required
from exts import db
from models import User, Question, Answer

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        # 查询数据库所有数据并排序 倒序按时间
        "questions": Question.query.order_by(Question.create_time.desc()).all()
    }
    # 数据渲染回前端
    return render_template("index.html", **context)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        check = request.form.get("check")
        user = User.query.filter(User.email == email).first()
        if user and user.check_password(password):
            # cookie 操作
            session["user_id"] = user.id
            # token 操作
            if check:
                session.permanent = True
            return redirect(url_for("index"))
        else:
            return u"邮箱或密码错误"


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        # 邮箱验证 判断是否注册
        user = User.query.filter(User.email == email).first()
        if user:
            return u"已被注册"
        else:
            # 判断密码是否一致
            if password != confirmPassword:
                return u"密码不一致"
            else:
                user = User(email=email, username=username, password=password)
                # 添加到事务
                db.session.add(user)
                # 提交事务
                db.session.commit()
                # 跳转到登录页面
                return redirect(url_for("login"))


# 钩子函数
@app.context_processor
def my_context_processor():
    # 获取用户session
    if hasattr(g, "user"):
        return {"user": g.user}
    return {}


@app.before_request
def my_before_request():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user


@app.route("/logout/")
def logout():
    # session.pop("user_id")
    # del session["user_id"]
    session.clear()
    return redirect(url_for("login"))


@app.route("/question/", methods=["GET", "POST"])
@login_required
def question():
    if request.method == "GET":
        return render_template("question.html")
    else:
        # 获取title
        title = request.form.get("title")
        # 获取content
        content = request.form.get("content")
        # 放入model
        question = Question(title=title, content=content)
        # 获取user_id=author
        question.author = g.user
        # 提交事务
        db.session.add(question)
        db.session.commit()
        # 跳转首页
        return redirect(url_for("index"))


@app.route("/detail/<question_id>")
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    count = len(question_model.answers)
    return render_template("detail.html", question=question_model, count=count)


@app.route("/add_answer/", methods=["POST"])
@login_required
def add_answer():
    content = request.form.get("answer_content")
    question_id = request.form.get("question_id")

    answer = Answer(content=content)

    answer.author = g.user

    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question

    db.session.add(answer)
    db.session.commit()
    return redirect(url_for("detail", question_id=question_id))


#
@app.route("/search/")
def search():
    query = request.args.get("query")
    # title或content or_()
    condition = or_(Question.title.contains(query), Question.content.contains(query))
    questions = Question.query.filter(condition).order_by(Question.create_time.desc())
    return render_template("index.html", questions=questions)


if __name__ == '__main__':
    app.run()

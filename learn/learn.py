import os
from flask import Flask, request, current_app, make_response, redirect, abort, render_template, session, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# 设置对应的密钥, 避免csrf攻击, 这是给wtf设置的
app.config['SECRET_KEY'] = 'hard to guess string'

# 配置email需要的参数
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
print(os.environ.get('MAIL_USERNAME'))
print(os.environ.get('MAIL_PASSWORD'))
# 使用邮件
mail = Mail(app)

# 使用flask-script可以使用命令行启动的时候参数来设置
# 注意如果使用的话, 要设置启动参数, 比如runserver --host x.x.x.x
manager = Manager(app)

# 配置对应的bootstrap, 这样可以使用对应的bootstrap模版
bootstrap = Bootstrap(app)

# 配置对应的数据库的信息
app.config["SQLALCHEMY_DATABASE_URI"] = u"mysql+pymysql://root:@localhost/flask"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

# db.create_all()

# request 请求上下文, 请求对象, 封装客户的http请求的内容
# session 请求上下文, 用户会话, 存储请求之间的字典
# g 程序上下文, 处理请求时候的临时存储对象, 每次请求都会重设这个变量
# current_app 程序上下文, 表示激活程序的程序实例


# WTForms支持的html标准字段
# StringField           文本字段
# TextAreaField         多行文本字段
# PasswordField         密码文本字段
# HiddenField           隐藏文本字段
# DateField             文本字段, 值为datetime.date格式
# DateTimeField         文本字段, 值为datetime.datetime格式
# IntegerField          文本字段, 值为整数
# DecimalField          文本字段, 值为decimal.Decimal
# FloatField            文本字段, 值为浮点数
# BooleanField          复选框, 值为True或False
# RadioField            一组单选框
# SelectField           下拉列表
# SelectMultipleField   下拉列表, 可选择多个值
# FileField             文件上传字段
# SubmitField           表单提交按钮
# FormField             把表单作为字段嵌入另一个表单
# FieldList             一组指定类型的字段

# WTForms验证函数
# Email                 验证电子邮件地址
# EqualTo               比较
# IPAddress             验证IPv4网络地址
# Length                验证输入字符串的长度
# NumberRange           验证输入的值在数字范围内
# Optional              无输入值时跳过其他验证函数
# Required(DataRequired)确保字段中有数据
# Regexp                使用正则表达式验证输入值
# URL                   验证URL
# AnyOf                 确保输入值在可选值列表中
# NoneOf                确保输入值不在可选值列表中


class NameForm(Form):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role")

    def __repr__(self):
        return "<Role {}>".format(self.name)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.INTEGER, db.ForeignKey("roles.id"))

    def __repr__(self):
        return "<User {}>".format(self.username)


# 下面这种叫view视图函数, 负责响应对应的请求
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get("name")
        if old_name is not None and old_name != form.name.data:
            flash("Looks lise you have change your name")
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('bootstrap-index.html', form=form, name=session.get("name"))


@app.route('/sql', methods=['GET', 'POST'])
def sql():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['know'] = False
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        # url_for 里面是重定向到的函数名
        return redirect(url_for('sql'))
    return render_template('bootstrap-index.html', form=form, name=session.get('name'), known=session.get('know', False))


# 下面这种叫view视图函数, 负责响应对应的请求
@app.route('/agent')
def hello_world():
    user_agent = request.headers.get("User-Agent")
    return 'Your agent {}'.format(user_agent)


@app.route('/make_response')
def make_resp():
    # 构造response然后返回
    response = make_response('<h1>have cookie!</h1>')
    # 设置cookie
    response.set_cookie('answer', '42')
    return response


@app.route('/redirect')
def redi():
    # 重定向
    return redirect("http://www.zhihu.com")


@app.route('/current_name')
def current_name():
    # current_app.name 这个项目的名字
    return 'current name {}'.format(current_app.name)


@app.route("/404")
def page_404():
    # 访问对应的页面表示是404
    abort(404)
    return


@app.route("/extends")
def extends():
    return render_template("extends.html")


@app.route('/400')
def bad_quest():
    # 后面的是返回的状态码
    return "400 page hehe", 400


# route是配置对应的url对应的使用的函数, <>是对应的参数
@app.route('/user/<name>')
def user_name(name):
    # return "<h1>Hello, your name is {}</h1>".format(name)
    return render_template("bootstrap-user.html", name=name)


@app.route('/template_index')
def template_index():
    # 使用简单的渲染模版, 不带参数
    return render_template("template_index.html")


@app.route('/template_user/<name>')
def template_user(name):
    # 使用渲染模版, 后面是带着参数是dict
    list_data = ["one", "two", "three", "four", "five"]
    return render_template("template_user.html", name=name, comments=list_data)


# 错误处理 404
@app.errorhandler(404)
def page_not_page(e):
    return render_template('404.html'), 404


# 错误处理 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # 开启debug模式
    # app.run(debug=True)

    # 发送对应的邮件
    # msg = Message("flask", sender='wxwangtju@gmail.com', recipients=['1131785625@qq.com', 'wxwang@tju.edu.cn'])
    # msg.body = 'text body'
    # msg.html = '<b>html</b> body'
    # with app.app_context():
    #     mail.send(msg)

    manager.run()
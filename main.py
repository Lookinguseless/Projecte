from flask import Flask, redirect, jsonify, request
from flask import render_template
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_unauthorized, current_user
# from werkzeug import secure_filename
import os
import random
import requests
# from data import __all_models
# might be used in db_session, commented at the moment

from data.post import Post
from data.users import User
from data.comments import Comments
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.AddingForm import AddingForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rigeldev_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/data.db")


@app.route('/index')
@app.route('/')
def index():
    db_sess = db_session.create_session()
    dbdata = db_sess.query(Post).all()
    datalist = []
    commentlist = []
    for j in dbdata:
        id = j.id
        dataobj = {"id": id, "title": j.title, "content": j.content, "commentable": j.commentable,
                   "author": db_sess.query(User).filter(User.id == j.author).first().name}
        dbcomdata = db_sess.query(Comments).filter(Comments.parent == id).all()
        for i in dbcomdata:
            commentlist.append({"author": i.author, "content": i.content})
        dataobj['comments'] = commentlist
        datalist.append(dataobj)
        commentlist = []

    return render_template('index.html', datalist=datalist)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/created', methods=['GET'])
def created():
    return render_template('created.html', title='Готово')


@login_required
@app.route('/add_new', methods=['GET', 'POST'])
def add_new():
    form = AddingForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post(
            title=form.title.data,
            content=form.content.data,
            commentable=form.commentable.data,
            author=current_user.id
        )
        db_sess.add(post)
        db_sess.commit()
        return redirect('/created')

    return render_template('Adder.html', title='Добавить новость', form=form)


@app.route('/check')
def check():
    db_sess = db_session.create_session()
    print(current_user.id)
    return 'check'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run()

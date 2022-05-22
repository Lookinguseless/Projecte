from flask import Flask, redirect, jsonify, request
from flask import render_template
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_unauthorized, \
    current_user
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
from forms.CommentingForm import CommentingForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rigeldev_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/data.db")

access_levels = ['Ученик', 'Учитель', 'Администратор']


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
            commentlist.append({"author": db_sess.query(User).filter(User.id == i.author).first().name,
                                "content": i.content, "id": i.id})
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
            access_level=0
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


@app.route('/deleted', methods=['GET'])
def deleted():
    return render_template('deleted.html', title='Готово')


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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/level_management')
def level_management():
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.id == current_user.id).first().access_level > 1:

        # access_levels

        users = db_sess.query(User).all()
        userlist = []
        for j in users:
            data = {'access_level': j.access_level, 'email': j.email,
                    'name': j.name, 'id': j.id}
            userlist.append(data)
        return render_template('admin.html', userlist=userlist, access_levels=access_levels,
                               leng=len(access_levels) - 1)
    else:
        return 'Нет доступа'


@login_required
@app.route('/level_ch/<type>/<id>')
def level_ch(type, id):
    db_sess = db_session.create_session()

    if current_user.id == id:
        return 'Нет доступа'

    if db_sess.query(User).filter(User.id == current_user.id).first().access_level > 1:
        affected_user = db_sess.query(User).filter(User.id == id).first()
        if type == 'up':
            if affected_user.access_level < len(access_levels) - 1:
                affected_user.access_level += 1
        elif type == 'down':
            if affected_user.access_level > 0:
                affected_user.access_level -= 1
        else:
            return 'Ошибка'
        db_sess.commit()
        data = {'access_level': affected_user.access_level, 'email': affected_user.email,
                'name': affected_user.name}
        return render_template('user up.html', data=data, access_levels=access_levels)


@login_required
@app.route('/add_comment/<post_id>', methods=['GET', 'POST'])
def add_comment(post_id):
    form = CommentingForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comments(
            content=form.content.data,
            parent=post_id,
            author=current_user.id
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect('/created')

    return render_template('addComment.html', title='Комментирование', form=form)


@login_required
@app.route('/delete/<post_id>', methods=['GET', 'POST'])
def delete(post_id):
    db_sess = db_session.create_session()

    content = db_sess.query(Post).filter(Post.id == post_id).first().content

    return render_template('delete.html', content=content, post_id=post_id)


@login_required
@app.route('/remove/<post_id>', methods=['GET', 'POST'])
def remove(post_id):
    if current_user.access_level > 1:
        db_sess = db_session.create_session()
        db_sess.query(Post).filter(Post.id == post_id).delete()
        db_sess.query(Comments).filter(Comments.parent == post_id).delete()
        db_sess.commit()

        return redirect('/deleted')


@login_required
@app.route('/remove_comm/<comment_id>', methods=['GET', 'POST'])
def remove_comm(comment_id):
    if current_user.access_level > 1:
        db_sess = db_session.create_session()
        db_sess.query(Comments).filter(Comments.id == comment_id).delete()
        db_sess.commit()

        return redirect('/deleted')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run()

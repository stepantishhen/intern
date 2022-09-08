import json
import requests

from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.users import User
from data.jobs import Jobs, Category, Cities

app = Flask(__name__)
app.config['SECRET_KEY'] = 'intern_app'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).order_by(Category.name)
    cities = db_sess.query(Cities).order_by(Cities.name)
    same_jobs = db_sess.query(Jobs).limit(3)
    if request.method == 'POST':
        return redirect(f"/job_search/?category={request.form.get('category')}&city={request.form.get('city')}&job={request.form.get('job')}")
    return render_template("index.html", categories=categories, cities=cities, same_jobs=same_jobs)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/blog")
def blog():
    return render_template("blog-home.html")


@app.route("/contacts")
def contacts():
    return render_template("contact-us.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == request.form.get('email')).first():
            return render_template('registration.html', message="Ты уже зареган")
        elif request.form.get('password') != request.form.get('check_password'):
            return render_template('registration.html', message="Не совпадают")
        else:
            user = User(
                first_name=request.form.get('first_name'),
                second_name=request.form.get('second_name'),
                email=request.form.get('email'),
            )
            user.set_password(request.form.get('password'))
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
    return render_template("registration.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect("/job_search")
        return render_template('login.html', message="Wrong login or password")
    return render_template('login.html')


@app.route("/job_search", methods=['GET', 'POST'])
def job_search():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).order_by(Category.name)
    cities = db_sess.query(Cities).order_by(Cities.name)
    if request.method == 'POST':
        jobs = db_sess.query(Jobs).filter(Jobs.category == request.form.get('category'),
                                          Jobs.city == request.form.get('city'),
                                          request.form.get('job') == Jobs.job_name)
        return render_template("job-search.html", jobs=jobs, categories=categories, cities=cities)
    return render_template("job-search.html", jobs=db_sess.query(Jobs), categories=categories, cities=cities)


@app.route("/job_single/<int:id>")
def job_single(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(id)
    return render_template("job-single.html", job=job)


@app.route("/add_job", methods=['GET', 'POST'])
def add_job():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    cities = db_sess.query(Cities).all()
    if request.method == 'POST':
        db_sess = db_session.create_session()
        jobs = Jobs(
            job_name=request.form.get('job_name'),
            city=request.form.get('city'),
            category=request.form.get('category'),
            description=request.form.get('description')
        )
        db_sess.add(jobs)
        db_sess.commit()
    return render_template('add_job.html', categories=categories, cities=cities)


@app.route("/add_category", methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        category = Category(name=request.form.get('name'))
        db_sess.add(category)
        db_sess.commit()
    return render_template('add_category.html')


def main():
    db_session.global_init("db/intern.sqlite")
    app.run(debug=True)


if __name__ == '__main__':
    main()

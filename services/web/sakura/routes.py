from flask import render_template, send_from_directory, flash, redirect, url_for
from . import app
from .forms import LoginForm


@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('hello_world'))
    return render_template('login.html', title='Вход', form=form)
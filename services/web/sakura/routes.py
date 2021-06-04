from flask import render_template, send_from_directory, flash, redirect, url_for, request
from . import app, db
from .forms import LoginForm, HairdresserForm
from flask_login import current_user, login_user, logout_user, login_required
from .models import User, Hairdresser


@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('admin'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/admin')
@login_required
def admin():
    hairdresser_form = HairdresserForm()
    return render_template('admin.html', title='Админ', hairdresser_form=hairdresser_form)


@app.route('/admin/hairdresser')
@login_required
def hairdresser():
    hairdressers = Hairdresser.query.order_by(Hairdresser.id).all()
    return render_template('hairdresser.html', title='Мастера', hairdressers=hairdressers)


@app.route('/admin/hairdresser/<int:hairdresser_id>', methods=['GET', 'POST'])
@login_required
def hairdresser_detail(hairdresser_id):
    hairdresser = Hairdresser.query.get_or_404(hairdresser_id)
    form = HairdresserForm()
    if form.validate_on_submit():
        hairdresser.name = form.name.data
        hairdresser.dob = form.dob.data
        hairdresser.specialization = form.specialization.data
        hairdresser.is_available = form.is_available.data
        db.session.commit()
        flash(f'Данные мастера {hairdresser.name} успешно изменены.')
        return redirect(url_for('hairdresser'))
    elif request.method == 'GET':
        form.name.data = hairdresser.name
        form.dob.data = hairdresser.dob
        form.specialization.data = hairdresser.specialization
        form.is_available.data = hairdresser.is_available
    return render_template('hairdresser_detail.html', title=f'Мастер {hairdresser}',
                           hairdresser=hairdresser, form=form)


@app.route('/admin/hairdresser/<int:hairdresser_id>/delete')
@login_required
def delete_hairdresser(hairdresser_id):
    hairdresser = Hairdresser.query.get_or_404(hairdresser_id)
    db.session.delete(hairdresser)
    db.session.commit()
    flash(f'Запись о мастере {hairdresser.name} удалена.')
    return redirect(url_for('hairdresser'))

@app.route('/admin/hairdresser/add', methods=['GET', 'POST'])
@login_required
def add_hairdresser():
    form = HairdresserForm()
    form.is_available.data = True
    if form.validate_on_submit():
        hairdresser = Hairdresser(name = form.name.data, dob = form.dob.data,
                                  specialization = form.specialization.data,
                                  is_available = form.is_available.data)
        db.session.add(hairdresser)
        db.session.commit()
        flash(f'Мастер {hairdresser.name} успешно добавлен.')
        return redirect(url_for('hairdresser'))
    return render_template('hairdresser_add.html', title='Новый мастер', form=form)
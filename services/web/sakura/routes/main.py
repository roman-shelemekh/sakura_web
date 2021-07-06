from flask import (
    render_template, send_from_directory, redirect, url_for, request, jsonify, abort, send_file
)
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from sqlalchemy import func
from sakura import app, db
from sakura.forms import LoginForm
from sakura.models import User, Hairdresser, Salon, Calendar, Shifts, Appointment, ServiceToAppointment
from sakura.utils import months_to_navigate, month_for_heading, is_fetch
from sakura.xlsx import create_xlsx


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/")
def index():
    return redirect('login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
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


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST' and request.form.get('date'):
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        salon_translit = Salon.query.order_by(Salon.id).first().translit
        return redirect(url_for('day_record', salon_translit=salon_translit, year=date.year, month=date.month,
                                day=date.day))
    return render_template('hello.html', title='Главная')


@app.route('/admin/schedule/<salon_translit>/<int:year>/<int:month>')
@login_required
def schedule(year, month, salon_translit):
    salon = Salon.query.filter(Salon.translit == salon_translit).first_or_404()
    salons = Salon.query.all()
    hairdressers = Hairdresser.query.filter(Hairdresser.is_available == True).all()
    dates = Calendar().month(year, month)
    return render_template('schedule.html', title='График работы', dates=dates, salon_translit=salon_translit,
                           salons=salons, month_for_heading=month_for_heading(year, month), salon_id=salon.id,
                           hairdressers=hairdressers, months_to_navigate=months_to_navigate(year, month))


@app.route('/admin/schedule/add', methods=['POST'])
@is_fetch
def add_shift():
    data = request.get_json()
    date = datetime.strptime(data.get('date'), '%d.%m.%Y')
    date_id = Calendar.query.filter(Calendar.date == date).first().id
    shift = Shifts(salon_id=data.get('salon_id'), hairdresser_id=data.get('hairdresser_id'), date_id=date_id)
    db.session.add(shift)
    try:
        db.session.commit()
        return jsonify(success=True)
    except:
        db.session.rollback()
        return jsonify(success=False)


@app.route('/admin/schedule/delete', methods=['POST'])
@is_fetch
def delete_shift():
    data = request.get_json()
    date = datetime.strptime(data.get('date'), '%d.%m.%Y')
    date_id = Calendar.query.filter(Calendar.date == date).first().id
    shift = Shifts.query.filter(Shifts.salon_id == int(data.get('salon_id')),
                                Shifts.hairdresser_id == int(data.get('hairdresser_id')),
                                Shifts.date_id == int(date_id)).first()
    db.session.delete(shift)
    try:
        db.session.commit()
        return jsonify(success=True)
    except IntegrityError:
        db.session.rollback()
        return jsonify(success=False)


@app.route('/admin/schedule/<salon_translit>/<int:year>/<int:month>/<int:day>')
@login_required
def day_record(year, month, day, salon_translit):
    salon = Salon.query.filter(Salon.translit == salon_translit).first_or_404()
    salons = Salon.query.all()
    try:
        date = datetime(year, month, day)
    except ValueError:
        abort(404)
    date = Calendar.query.filter(Calendar.date == date).first_or_404()
    revenue = Appointment.query.with_entities(func.sum(ServiceToAppointment.final_price)).select_from(Appointment) \
        .join(ServiceToAppointment).filter(Appointment.accomplished == True, Appointment.date == date.date,
                                           Appointment.salon_id == salon.id).first()[0]
    hairdresser_to_shift = [shift.hairdresser_shifts for shift in
                            Shifts.query.filter(Shifts.date_id == date.id, Shifts.salon_id == salon.id)]
    hairdressers = []
    for hairdresser in hairdresser_to_shift:
        try:
            s = db.session.query(func.sum(ServiceToAppointment.final_price)).select_from(Hairdresser)\
                .outerjoin(Appointment).outerjoin(ServiceToAppointment).group_by(Hairdresser)\
                .filter(Appointment.date == date.date, Appointment.salon_id == salon.id, Hairdresser.id == hairdresser.id,
                        Appointment.accomplished == True, Appointment.salon_id == salon.id).first()[0]
        except TypeError:
            s = None
        hairdressers.append((hairdresser, s))
    appointments = Appointment.query.with_entities(Appointment, func.sum(ServiceToAppointment.final_price)
                                                   .label('total_price')) \
        .outerjoin(ServiceToAppointment).group_by(Appointment.id).filter(Appointment.salon_id == salon.id)\
        .filter(Appointment.date == date.date).order_by(Appointment.time)
    if request.args.get('hairdresser', type=int):
        appointments = appointments.filter(Appointment.hairdresser_id == request.args.get('hairdresser', type=int))
    a_appointments = appointments.filter(Appointment.accomplished == True)
    na_appointments = appointments.filter(Appointment.accomplished.is_(False))
    appointments_count = Appointment.query.filter(Appointment.date == date.date)\
                                          .filter(Appointment.accomplished == True, Appointment.salon_id == salon.id)\
                                                                                                            .count()

    return render_template('day_record.html', title='Рабочий журнал', salons=salons, salon_id=salon.id,
                           salon_translit=salon_translit, date=date, hairdressers=hairdressers, revenue=revenue,
                           appointments=a_appointments.all(), na_appointments=na_appointments.all(),
                           appointments_count=appointments_count)


@app.route('/admin/schedule/<salon_translit>/<int:year>/<int:month>/<int:day>/xlsx')
@login_required
def xlsx(year, month, day, salon_translit):
    salon = Salon.query.filter(Salon.translit == salon_translit).first_or_404()
    try:
        date = datetime(year, month, day)
    except ValueError:
        abort(404)
    date = Calendar.query.filter(Calendar.date == date).first_or_404()
    revenue = Appointment.query.with_entities(func.sum(ServiceToAppointment.final_price)).select_from(Appointment) \
        .join(ServiceToAppointment).filter(Appointment.accomplished == True, Appointment.date == date.date,
                                           Appointment.salon_id == salon.id).first()[0]
    hairdresser_to_shift = [shift.hairdresser_shifts for shift in
                            Shifts.query.filter(Shifts.date_id == date.id, Shifts.salon_id == salon.id)]
    hairdressers = []
    for hairdresser in hairdresser_to_shift:
        try:
            s = db.session.query(func.sum(ServiceToAppointment.final_price)).select_from(Hairdresser) \
                .outerjoin(Appointment).outerjoin(ServiceToAppointment).group_by(Hairdresser) \
                .filter(Appointment.date == date.date, Appointment.salon_id == salon.id,
                        Hairdresser.id == hairdresser.id,
                        Appointment.accomplished == True, Appointment.salon_id == salon.id).first()[0]
        except TypeError:
            s = None
        hairdressers.append((hairdresser, s))
    appointments = Appointment.query.with_entities(Appointment, func.sum(ServiceToAppointment.final_price)
                                                   .label('total_price')) \
        .outerjoin(ServiceToAppointment).group_by(Appointment.id).filter(Appointment.salon_id == salon.id) \
        .filter(Appointment.date == date.date).order_by(Appointment.time).filter(Appointment.accomplished == True)
    path = create_xlsx(date, salon, appointments, hairdressers, appointments.count(), revenue)
    print(path)
    return send_file(path)

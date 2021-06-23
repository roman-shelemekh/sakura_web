from flask import (
    render_template, send_from_directory, flash, redirect, url_for, request, jsonify, abort
)
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_user, logout_user, login_required
from . import app, db
from .forms import (
    LoginForm, HairdresserForm, SalonForm, ServiceForm, TypeForm, ClientForm, AppointmentFilterForm,
    AppointmentForm
)
from .models import (
    User, Hairdresser, Salon, Service, Type, Calendar, Shifts, Client, Appointment, ServiceToAppointment
)
from .utils import months_to_navigate, month_for_heading, is_fetch
from datetime import datetime
from transliterate import translit
from sqlalchemy import func


@app.route("/")
def index():
    users = User.query.all()
    return redirect('login')


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


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


@app.route('/admin/hairdresser')
@login_required
def hairdresser():
    hairdressers = Hairdresser.query.order_by(Hairdresser.id).all()
    return render_template('hairdresser.html', title='Мастера', hairdressers=hairdressers)


@app.route('/admin/hairdresser/<int:hairdresser_id>', methods=['GET', 'POST'])
@login_required
def hairdresser_detail(hairdresser_id):
    hairdresser = Hairdresser.query.get_or_404(hairdresser_id)
    form = HairdresserForm(edit=True)
    form.specialization.choices = [(str(row.id), row.name + ' (' + row.service_type.name + ')') for row in
                                   Service.query.order_by(Service.type_id).all()]
    if form.validate_on_submit():
        hairdresser.name = form.name.data
        hairdresser.dob = form.dob.data
        hairdresser.comment = form.comment.data
        hairdresser.is_available = form.is_available.data
        hairdresser.specialization = [Service.query.get(int(i)) for i in form.specialization.data]
        db.session.commit()
        flash(f'Данные мастера {hairdresser.name} успешно изменены.')
        return redirect(url_for('hairdresser'))
    elif request.method == 'GET':
        form.specialization.data = [str(i.id) for i in hairdresser.specialization]
        # form.process()
        form.name.data = hairdresser.name
        form.dob.data = hairdresser.dob
        form.comment.data = hairdresser.comment
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
    form.specialization.choices = [(str(row.id), row.name + ' (' + row.service_type.name + ')') for row in Service.query.all()]
    if form.validate_on_submit():
        hairdresser = Hairdresser(name=form.name.data, dob=form.dob.data,
                                  comment=form.comment.data,
                                  is_available=form.is_available.data)
        hairdresser.specialization = [Service.query.get(int(i)) for i in form.specialization.data]
        db.session.add(hairdresser)
        db.session.commit()
        flash(f'Мастер {hairdresser.name} успешно добавлен.')
        return redirect(url_for('hairdresser'))
    return render_template('hairdresser_add.html', title='Новый мастер', form=form)


@app.route('/admin/salon')
@login_required
def salon():
    salons = Salon.query.order_by(Salon.id).all()
    return render_template('salon.html', title='Парикмахерские', salons=salons)


@app.route('/admin/salon/<salon_translit>', methods=['GET', 'POST'])
@login_required
def salon_detail(salon_translit):
    salon = Salon.query.filter(Salon.translit == salon_translit).first_or_404()
    form = SalonForm(edit=True)
    if form.validate_on_submit():
        salon.name = form.name.data
        salon.address = form.address.data
        salon.phone_number = form.phone_number.data
        salon.latitude = form.latitude.data
        salon.longitude = form.longitude.data
        db.session.commit()
        flash(f'Данные о парикмахерской "{salon.name}" успешно изменены.')
        return redirect(url_for('salon'))
    elif request.method == 'GET':
        form.name.data = salon.name
        form.address.data = salon.address
        form.phone_number.data = salon.phone_number
        form.latitude.data = salon.latitude
        form.longitude.data = salon.longitude
    return render_template('salon_detail.html', title=f'Парикмахерская "{salon}"',
                           salon=salon, form=form)


@app.route('/admin/salon/<salon_translit>/delete')
@login_required
def delete_salon(salon_translit):
    salon = Salon.query.filter(Salon.translit == salon_translit).first_or_404()
    db.session.delete(salon)
    db.session.commit()
    flash(f'Запись о парикмахерской "{salon.name}" удалена.')
    return redirect(url_for('salon'))


@app.route('/admin/salon/add', methods=['GET', 'POST'])
@login_required
def add_salon():
    form = SalonForm()
    if form.validate_on_submit():
        name_translit = translit(form.name.data, 'ru', reversed=True).replace(' ', '_').replace('.', '').lower()
        salon = Salon(name=form.name.data, address = form.address.data, phone_number=form.phone_number.data,
                      latitude=form.latitude.data, longitude=form.longitude.data, translit=name_translit)
        db.session.add(salon)
        db.session.commit()
        flash(f'Парикмахерская "{salon.name}" успешно добавлена.')
        return redirect(url_for('salon'))
    return render_template('salon_add.html', title='Новая парикмахерская', form=form)


@app.route('/admin/service')
@login_required
def service():
    types = Type.query.all()
    services = Service.query.order_by(Service.id).all()
    return render_template('service.html', title='Услуги', serviсes=services, types=types)


@app.route('/admin/service/type/<int:type_id>')
@login_required
def service_by_type(type_id):
    types = Type.query.all()
    service_type = Type.query.get_or_404(type_id)
    delete_type = request.path
    return render_template('service.html', title=service_type.name.capitalize(), serviсes=service_type.services, types=types,
                           delete_type=delete_type)

@app.route('/admin/service/type/<int:type_id>/delete')
@login_required
def delete_type(type_id):
    service_type = Type.query.get_or_404(type_id)
    db.session.delete(service_type)
    db.session.commit()
    flash(f'Тип услуг "{service_type.name}" успешно удалем.')
    return redirect(url_for('service'))


@app.route('/admin/service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(edit=True)
    form.type.choices = [(str(row.id), row.name) for row in Type.query.all()]
    if form.validate_on_submit():
        service.name = form.name.data.capitalize()
        service.price = form.price.data
        service.type_id = form.type.data
        db.session.commit()
        flash(f'Услуга {service.name} успешно изменена.')
        return redirect(url_for('service'))
    elif request.method == 'GET':
        form.type.default = service.type_id
        form.process()
        form.name.data = service.name
        form.price.data = service.price
    return render_template('service_detail.html', title=f'Услуга {service.name}',
                           service=service, form=form)


@app.route('/admin/service/add', methods=['GET', 'POST'])
@login_required
def add_service():
    form = ServiceForm()
    form.type.choices = [(str(row.id), row.name) for row in Type.query.all()]
    if form.validate_on_submit():
        service = Service(name=form.name.data.capitalize(), price=form.price.data, type_id=form.type.data)
        db.session.add(service)
        db.session.commit()
        flash(f'Услуга {service.name} успешно добавлена.')
        return redirect(url_for('service'))
    return render_template('service_add.html', title='Новая услуга', form=form)


@app.route('/admin/service/<int:service_id>/delete')
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash(f'Услуга "{service.name.capitalize()}" удалена.')
    return redirect(url_for('service'))


@app.route('/admin/service/type/add', methods=['GET', 'POST'])
@login_required
def service_type_add():
    form = TypeForm()
    if form.validate_on_submit():
        type = Type(name=form.name.data.lower())
        db.session.add(type)
        db.session.commit()
        flash(f'Тип услуг {type.name} успешно добавлен.')
        return redirect(url_for('service'))
    return render_template('service_type_add.html', title='Новый тип услуг', form=form)


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


@app.route('/admin/client')
@login_required
def client():
    clients = Client.query.all()
    return render_template('client.html', title='Клиенты', clients=clients)


@app.route('/admin/client/add', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientForm()
    if request.args.get('phone_number'):
        form.phone_number.data = '+' + request.args.get('phone_number').strip()
    if form.validate_on_submit():
        client = Client(name=form.name.data, phone_number=form.phone_number.data, discount=form.discount.data)
        db.session.add(client)
        db.session.commit()
        flash(f'Клиент "{client.name}" успешно добавлен.')
        return redirect(url_for('client'))
    return render_template('client_add.html', title='Новый клиент', form=form)


@app.route('/admin/client/<int:client_id>/update', methods=['GET', 'POST'])
@login_required
def client_update(client_id):
    client = Client.query.get_or_404(client_id)
    form = ClientForm(edit=True)
    if form.validate_on_submit():
        client.name = form.name.data
        client.phone_number = form.phone_number.data
        client.discount = form.discount.data
        db.session.commit()
        flash(f'Данные о клиенте "{client.name}" успешно изменены.')
        return redirect(url_for('client_detail', client_id=client_id))
    elif request.method == 'GET':
        form.name.data = client.name
        form.phone_number.data = client.phone_number
        form.discount.data = client.discount
    return render_template('client_update.html', title=f'Клиент {client.name}',
                           client=client, form=form)


@app.route('/admin/client/<int:client_id>/delete')
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash(f'Запись о клиенте "{client.name}" удалена.')
    return redirect(url_for('client'))


@app.route('/admin/client/<int:client_id>/')
@login_required
def client_detail(client_id):
    client = Client.query.get_or_404(client_id)
    appointments = Appointment.query.filter(Appointment.client_id == client.id).order_by(Appointment.date.desc())
    appointments_count = Appointment.query.filter(Appointment.client_id == client.id,
                                                  Appointment.accomplished == True).count()
    try:
        revenue = db.session.query(func.sum(ServiceToAppointment.final_price)).join(Appointment)\
            .group_by(Appointment.client_id)\
            .filter(Appointment.client_id == client_id).filter(Appointment.accomplished == True).first()[0]
    except TypeError:
        revenue = 0
    return render_template('client_detail.html', title='История посещений', client=client,
                           appointments=appointments, revenue=revenue, appointments_count=appointments_count)


@app.route('/admin/appointment/<salon_translit>')
@login_required
def all_appointments(salon_translit):
    salons = Salon.query.all()
    salon_id = Salon.query.filter(Salon.translit == salon_translit).first_or_404().id

    appointments = Appointment.query.with_entities(Appointment, func.sum(ServiceToAppointment.price).label('total_price'))\
        .outerjoin(ServiceToAppointment).group_by(Appointment.id).filter(Appointment.salon_id == salon_id)\
        .order_by(Appointment.date.desc()).order_by(Appointment.time.desc())

    hairdressers = Hairdresser.query.all()
    form = AppointmentFilterForm(request.args)
    form.hairdresser.choices = [('', '--выбрать--')] + [(i.id, i.name) for i in Hairdresser.query.all()]
    try:
        start = datetime.strptime(request.args.get('start'), '%Y-%m-%d')
    except (ValueError, TypeError):
        start = None
    try:
        end = datetime.strptime(request.args.get('end'), '%Y-%m-%d')
    except (ValueError, TypeError):
        end = None
    hairdresser = request.args.get('hairdresser', type=int)
    if request.args.get('status') in [i[0] for i in form.status.choices]:
        status = request.args.get('status')
    else:
        status = None
    form.hairdresser.default = hairdresser
    form.status.default = status or 'all'
    form.process()
    form.start.data = start
    form.end.data = end
    if start and end:
        appointments = appointments.filter(Appointment.date.between(start, end))
    if hairdresser and Hairdresser.query.get(hairdresser):
        appointments = appointments.filter(Appointment.hairdresser_id == int(hairdresser))
    if status == 'accomplished':
        appointments = appointments.filter(Appointment.accomplished)
    elif status == 'unaccomplished':
        appointments = appointments.filter(Appointment.accomplished.is_(False))
    page = request.args.get('page', 1, type=int)
    appointments = appointments.paginate(page, 30, False)
    return render_template('appointment.html', title='Посещения', appointments=appointments, form=form,
                           salons=salons, salon_id=salon_id, salon_translit=salon_translit,
                           hairdressers=hairdressers)

@app.route('/admin/appointment/<int:appointment_id>/')
@login_required
def appointment_detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    total = sum([service.final_price for service in appointment.services])
    return render_template('appointment_detail.html', title=f'Посещение № {appointment.id}', appointment=appointment,
                           total=total)


@app.route('/admin/appointment/<int:appointment_id>/update', methods=['GET', 'POST'])
@login_required
def appointment_update(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm(edit=True)
    form.salon.choices = [(str(row.id), row.name) for row in Salon.query.all()]
    form.client.choices = [(str(row.id), row.phone_number) for row in Client.query.all()]
    form.services.choices = [(str(row.id), row.name) for row in Service.query.all()]
    print(form.data)
    if form.validate_on_submit():
        appointment.date = form.date.data
        appointment.time = form.time.data
        appointment.salon_id = form.salon.data
        appointment.hairdresser_id = form.hairdresser.data or None
        client = Client.query.filter(Client.phone_number == form.client.data).first()
        appointment.client_id = client.id
        appointment.comment = form.comment.data
        appointment.accomplished = form.accomplished.data
        for service in appointment.services:
            db.session.delete(service)
        for service_id in form.services.data:
            service = ServiceToAppointment(service_id=service_id, appointment_id=appointment.id)
            service.set_price()
            db.session.add(service)
        db.session.commit()
        flash(f'Посещение № {appointment.id} от {appointment.date.strftime("%d.%m.%Y")} успешно изменено.')
        return redirect(url_for('appointment_detail', appointment_id=appointment.id))
    elif request.method == 'GET':
        form.salon.default = appointment.salon_id
        form.process()
        form.date.data = appointment.date
        form.time.data = appointment.time
        form.client.data = Client.query.get(appointment.client_id)
        form.comment.data = appointment.comment
        form.accomplished.data = appointment.accomplished
    return render_template('appointment_update.html', title=f'Посещение № {appointment.id}',
                           appointment=appointment, form=form)


@app.route('/admin/appointment/<int:appointment_id>/delete')
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash(f'Посещение от {appointment.date.strftime("%d.%m.%Y")} в '
          f'{appointment.time.strftime("%H:%M")} успешно удалено.')
    salon = Salon.query.get_or_404(appointment.salon_id)
    return redirect(url_for('all_appointments', salon_translit=salon.translit))


@app.route('/admin/appointment/get_data/<int:appointment_id>', methods=['POST'])
@is_fetch
def get_data(appointment_id):
    data = request.get_json()
    date_id = Calendar.query.filter(Calendar.date == datetime.strptime(data['date'], '%Y-%m-%d').date()).first().id
    shifts = Shifts.query.filter(Shifts.salon_id == data.get('salon_id'), Shifts.date_id == date_id).all()
    hairdressers = [{'id':shift.hairdresser_shifts.id, 'name': shift.hairdresser_shifts.name} for shift in shifts]
    default_hairdresser = Appointment.query.get(appointment_id).hairdresser_id
    default_services = [service.service_id for service in Appointment.query.get(appointment_id).services]
    if data.get('initial') and default_hairdresser:
        services = [{'id': service.id, 'name': service.name} for service
                    in Hairdresser.query.get(default_hairdresser).specialization]
    elif data.get('hairdresser_id'):
        services = [{'id': service.id, 'name': service.name} for service
                    in Hairdresser.query.get(data.get('hairdresser_id')).specialization]
        default_hairdresser = int(data.get('hairdresser_id'))
    else:
        services = [{'id': service.id, 'name': service.name} for service in Service.query.all()]
    return jsonify(clients=[i.phone_number for i in Client.query.all()], hairdressers=hairdressers,
                   default_hairdresser=default_hairdresser, services=services, default_services=default_services)


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
    hairdresser_to_shift = [shift.hairdresser_shifts for shift in Shifts.query.filter(Shifts.date_id == date.id)]
    hairdressers = []
    for hairdresser in hairdresser_to_shift:
        try:
            s = db.session.query(func.sum(ServiceToAppointment.final_price)).select_from(Hairdresser)\
                .outerjoin(Appointment).outerjoin(ServiceToAppointment).group_by(Hairdresser)\
                .filter(Appointment.date == date.date, Appointment.salon_id == 1, Hairdresser.id == hairdresser.id)\
                .first()[0]
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
                                          .filter(Appointment.accomplished == True).count()
    revenue = Appointment.query.with_entities(func.sum(ServiceToAppointment.final_price)).select_from(Appointment)\
        .join(ServiceToAppointment).filter(Appointment.date == date.date, Appointment.salon_id == salon.id).first()[0]
    return render_template('day_record.html', title='Рабочий журнал', salons=salons, salon_id=salon.id,
                           salon_translit=salon_translit, date=date, hairdressers=hairdressers,
                           appointments=a_appointments.all(), na_appointments=na_appointments.all(),
                           visitors=a_appointments.count(), revenue=revenue, appointments_count=appointments_count)


@app.route('/admin/appointment/add', methods=['GET', 'POST'])
@login_required
def appointment_add():
    form = AppointmentForm()
    if request.args.get('date'):
        form.date.data = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    form.salon.choices = [(str(row.id), row.name) for row in Salon.query.order_by(Salon.id).all()]
    form.services.choices = [(str(row.id), row.name) for row in Service.query.all()]
    if form.validate_on_submit():
        print(form.data)
        client = Client.query.filter(Client.phone_number == form.client.data).first()
        appointment = Appointment(date=form.date.data, time=form.time.data, client_id=client.id,
                                  salon_id=form.salon.data, hairdresser_id=form.hairdresser.data or None,
                                  comment=form.comment.data, accomplished=form.accomplished.data)
        db.session.add(appointment)
        db.session.commit()
        for service_id in form.services.data:
            service = ServiceToAppointment(service_id=service_id, appointment_id=appointment.id)
            service.set_price()
            db.session.add(service)
        db.session.commit()
        flash(f'Посещение № {appointment.id} от {appointment.date.strftime("%d.%m.%Y")} успешно добавлено.')
        return redirect(url_for('appointment_detail', appointment_id=appointment.id))
    return render_template('appointment_add.html', title=f'Новое посещение', form=form)


@app.route('/admin/appointment/get_data/', methods=['POST'])
@is_fetch
def add_get_data():
    data = request.get_json()
    print(data)
    hairdressers = None
    default_hairdresser = None
    services = [{'id': service.id, 'name': service.name} for service in Service.query.all()]
    if data.get('date'):
        date_id = Calendar.query.filter(Calendar.date == datetime.strptime(data['date'], '%Y-%m-%d').date()).first().id
        shifts = Shifts.query.filter(Shifts.salon_id == data.get('salon_id'), Shifts.date_id == date_id).all()
        hairdressers = [{'id': shift.hairdresser_shifts.id, 'name': shift.hairdresser_shifts.name} for shift in shifts]
        if data.get('hairdresser_id'):
            default_hairdresser = int(data.get('hairdresser_id'))
            services = [{'id': service.id, 'name': service.name} for service
                        in Hairdresser.query.get(default_hairdresser).specialization]
    return jsonify(clients=[i.phone_number for i in Client.query.all()], hairdressers=hairdressers,
                   default_hairdresser=default_hairdresser, services=services)


@app.route('/admin/appointment/get_clients/')
@is_fetch
def get_clients():
    return jsonify(clients=[i.phone_number for i in Client.query.all()])


@app.route('/admin/appointment/get_client_data/', methods=['POST'])
@is_fetch
def get_client_data():
    data = request.get_json()
    print(data)
    client = Client.query.filter(Client.phone_number == data.get('phone_number')).first()
    if client:
        return jsonify(client=client.id)
    else:
        return jsonify(client=False)
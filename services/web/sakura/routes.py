from flask import (
    render_template, send_from_directory, flash, redirect, url_for, request, jsonify
)
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_user, logout_user, login_required
from . import app, db
from .forms import LoginForm, HairdresserForm, SalonForm, ServiceForm, TypeForm, ClientForm, AppointmentFilterForm
from .models import User, Hairdresser, Salon, Service, Type, Calendar, Shifts, Client, Appointment
from .utils import months_to_navigate, month_for_heading
from datetime import datetime
from transliterate import translit


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
    if form.validate_on_submit():
        client = Client(name=form.name.data, phone_number=form.phone_number.data, discount=form.discount.data)
        db.session.add(client)
        db.session.commit()
        flash(f'Клиент "{client.name}" успешно добавлен.')
        return redirect(url_for('client'))
    return render_template('client_add.html', title='Новый клиент', form=form)


@app.route('/admin/client/<int:client_id>', methods=['GET', 'POST'])
@login_required
def client_detail(client_id):
    client = Client.query.get_or_404(client_id)
    form = ClientForm(edit=True)
    if form.validate_on_submit():
        client.name = form.name.data
        client.phone_number = form.phone_number.data
        client.discount = form.discount.data
        db.session.commit()
        flash(f'Данные о клиенте "{client.name}" успешно изменены.')
        return redirect(url_for('client'))
    elif request.method == 'GET':
        form.name.data = client.name
        form.phone_number.data = client.phone_number
        form.discount.data = client.discount
    return render_template('client_detail.html', title=f'Клиент {client.name}',
                           client=client, form=form)


@app.route('/admin/client/<int:client_id>/delete')
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash(f'Запись о клиенте "{client.name}" удалена.')
    return redirect(url_for('client'))


@app.route('/admin/appointment/<salon_translit>')
@login_required
def all_appointments(salon_translit):
    salons = Salon.query.all()
    salon_id = Salon.query.filter(Salon.translit == salon_translit).first_or_404().id
    appointments = Appointment.query.filter(Appointment.salon_id == salon_id).order_by(Appointment.date.desc())\
        .order_by(Appointment.time.desc())
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

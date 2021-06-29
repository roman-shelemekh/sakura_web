from flask import render_template,flash, redirect, url_for, request, jsonify
from flask_login import login_required
from datetime import datetime
from sqlalchemy import func
from sakura import app, db
from sakura.forms import AppointmentFilterForm, AppointmentForm
from sakura.utils import is_fetch
from sakura.models import (
    Hairdresser, Salon, Service, Calendar, Shifts, Client, Appointment, ServiceToAppointment
)


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
    form.services.choices = [(str(row.id), row.name + ' (' + row.service_type.name + ')') for row
                             in Service.query.all()]
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


@app.route('/admin/appointment/add', methods=['GET', 'POST'])
@login_required
def appointment_add():
    form = AppointmentForm()
    form.salon.choices = [(str(row.id), row.name) for row in Salon.query.order_by(Salon.id).all()]
    form.services.choices = [(str(row.id), row.name + ' (' + row.service_type.name + ')') for row
                             in Service.query.all()]
    if form.validate_on_submit():
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
    if request.args.get('salon_id'):
        form.salon.default = request.args.get('salon_id')
        form.process()
    if request.args.get('date'):
        form.date.data = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    return render_template('appointment_add.html', title=f'Новое посещение', form=form)


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
        services = [{'id': service.id, 'name': service.name + ' (' + service.service_type.name + ')'} for service
                    in Hairdresser.query.get(default_hairdresser).specialization]
    elif data.get('hairdresser_id'):
        services = [{'id': service.id, 'name': service.name + ' (' + service.service_type.name + ')'} for service
                    in Hairdresser.query.get(data.get('hairdresser_id')).specialization]
        default_hairdresser = int(data.get('hairdresser_id'))
    else:
        services = [{'id': service.id, 'name': service.name + ' (' + service.service_type.name + ')'} for service
                    in Service.query.all()]
    return jsonify(clients=[i.phone_number for i in Client.query.all()], hairdressers=hairdressers,
                   default_hairdresser=default_hairdresser, services=services, default_services=default_services)


@app.route('/admin/appointment/get_data/', methods=['POST'])
@is_fetch
def add_get_data():
    data = request.get_json()
    print(data)
    hairdressers = None
    default_hairdresser = None
    services = [{'id': service.id, 'name': service.name +' (' + service.service_type.name + ')'} for service in Service.query.all()]
    if data.get('date'):
        date_id = Calendar.query.filter(Calendar.date == datetime.strptime(data['date'], '%Y-%m-%d').date()).first().id
        shifts = Shifts.query.filter(Shifts.salon_id == data.get('salon_id'), Shifts.date_id == date_id).all()
        hairdressers = [{'id': shift.hairdresser_shifts.id, 'name': shift.hairdresser_shifts.name} for shift in shifts]
        if data.get('hairdresser_id'):
            default_hairdresser = int(data.get('hairdresser_id'))
            services = [{'id': service.id, 'name': service.name +' (' + service.service_type.name + ')'} for service
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
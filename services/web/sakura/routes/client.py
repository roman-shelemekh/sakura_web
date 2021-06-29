from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from sqlalchemy import func
from sakura import app, db
from sakura.forms import ClientForm
from sakura.models import Client, Appointment, ServiceToAppointment


@app.route('/admin/client')
@login_required
def client():
    page = request.args.get('page', 1, type=int)
    clients = Client.query.paginate(page, 30, False)
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

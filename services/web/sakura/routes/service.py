from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from sakura import app, db
from sakura.forms import ServiceForm, TypeForm
from sakura.models import Service, Type


@app.route('/admin/service')
@login_required
def service():
    types = Type.query.all()
    services = Service.query.order_by(Service.id).all()
    return render_template('service.html', title='Услуги', serviсes=services, types=types)


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



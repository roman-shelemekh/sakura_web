from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from sakura import app, db
from sakura.forms import HairdresserForm
from sakura.models import Hairdresser, Service


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
    form.specialization.choices = [(str(row.id), row.name + ' (' + row.service_type.name + ')') for row in
                                   Service.query.all()]
    form.specialization.default = [str(row.id) for row in Service.query.all()]
    form.process()
    form.is_available.data = True
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
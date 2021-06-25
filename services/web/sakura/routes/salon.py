from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from transliterate import translit
from sakura import app, db
from sakura.forms import SalonForm
from sakura.models import Salon


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


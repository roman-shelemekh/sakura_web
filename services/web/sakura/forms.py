from flask_wtf import FlaskForm
from wtforms import (
    widgets, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField,
    IntegerField, ValidationError, DateField, RadioField
)
from wtforms.validators import DataRequired, Length, Optional
from .models import User, Hairdresser, Salon, Client
from .utils import Unique, MyForm, MyDateField, MyFloatField, MyTimeField
from datetime import time


class LoginForm(FlaskForm):
    username = StringField('Пользователь', validators=[DataRequired(message='Обязательное поле.')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Обязательное поле.')])
    submit = SubmitField('Войти')

    def validate(self):
        val = super(LoginForm, self).validate(extra_validators=None)
        if not val:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user is None or not user.check_password(self.password.data):
            self.username.errors.append(' ')
            self.password.errors.append('Неправильное имя или пароль.')
            return False
        return True


class HairdresserForm(MyForm):
    name = StringField('Фамилия и имя',
                       validators=[Unique(object_class=Hairdresser, column='name',
                                          message='Мастер с таким именем уже существует.'),
                                   DataRequired(message='Обязательное поле.'),
                                   Length(min=0, max=128, message='Поле "Имя" не должно превышать 128 знаков.')])
    dob = MyDateField('День рождения', validators=[Optional()], format='%d.%m.%Y')
    comment = TextAreaField('Комментарий', validators=[Length(
                                                        min=0, max=500,
                                                        message='Поле "Комментарий" не должно превышать 500 знаков.')])
    is_available = BooleanField('Статус')
    specialization = SelectMultipleField('Специализация мастера', widget=widgets.ListWidget(prefix_label=False),
                                         option_widget=widgets.CheckboxInput())


class SalonForm(MyForm):
    name = StringField('Название',
                       validators=[Unique(object_class=Salon, column='name',
                                          message='Парикмахерская с таким названием уже существует.'),
                                   DataRequired(message='Обязательное поле.'),
                                   Length(min=0, max=128, message='Поле "Название" не должно превышать 128 знаков.')])
    address = StringField('Адрес',
                          validators=[Unique(object_class=Salon, column='address',
                                             message='Парикмахерская с таким адресом уже существует.'),
                                      DataRequired(message='Обязательное поле.'),
                                      Length(min=0, max=128, message='Поле "Название" не должно превышать 128 знаков.')]
                          )
    phone_number = StringField('Номер телефона', validators=[Length(min=0, max=13,
                                                 message='Поле "Номер телефона" не должно '
                                                         'превышать 13 знаков (+375XXXXXXXXX).')])
    latitude = MyFloatField('Широта', validators=[Optional()])
    longitude = MyFloatField('Долгота', validators=[Optional()])

    def validate(self):
        val = super(SalonForm, self).validate(extra_validators=None)
        if not val:
            return False
        salon = Salon.query.filter_by(latitude=self.latitude.data, longitude=self.longitude.data).first()
        if salon is not None:
            self.latitude.errors.append(' ')
            self.longitude.errors.append('Парикмахерская с такими координатами уже существует.')
            return False
        return True


class ServiceForm(MyForm):
    name = StringField('Название',
                       validators=[DataRequired(message='Обязательное поле.'),
                                   Length(min=0, max=128, message='Поле "Название" не должно превышать 128 знаков.')])
    price = MyFloatField('Цена', validators=[Optional()])
    type = SelectField('Тип')


class TypeForm(MyForm):
    name = StringField('Название',
                       validators=[DataRequired(message='Обязательное поле.'),
                                   Length(min=0, max=40, message='Поле "Название" не должно превышать 40 знаков.')])


class ClientForm(MyForm):
    name = StringField('Имя', validators=[DataRequired(message='Обязательное поле.'),
                                          Length(min=0, max=128,
                                                 message='Поле "Имя" не должно превышать 128 знаков.')])
    phone_number = StringField('Номер телефона',
                               validators=[Unique(object_class=Client, column='phone_number',
                                                  message='Клиент с таким номером телефона уже существует.'),
                                           Length(min=0, max=13, message='Поле "Номер телефона" не должно '
                                                                         'превышать 13 знаков (+375XXXXXXXXX).')])
    discount = IntegerField('Скидка', validators=[Optional()])

    def validate_discount(form, field):
        if field.data and field.data > 100:
            raise ValidationError('Скидка не может быть более 100%.')


class AppointmentFilterForm(MyForm):
    start = MyDateField('Начало', validators=[Optional()], format='%Y-%m-%d')
    end = MyDateField('Конец', validators=[Optional()])
    hairdresser = SelectField('Мастер')
    status = RadioField('Статус', choices=[
        ('accomplished', 'состоявшиеся'), ('unaccomplished', 'несостоявшиеся'), ('all', 'все'),
    ])

class AppointmentForm(MyForm):
    date = MyDateField('Дата', validators=[DataRequired('Поле "Дата" является обязательным для заполнения')],
                       format='%Y-%m-%d')
    time = MyTimeField('Дата', validators=[Optional()], format='%H:%M')
    salon = SelectField('Парикмахерская')
    client = StringField('Клиент')
    hairdresser = SelectField('Мастер', validate_choice=False)
    comment = TextAreaField('Комментарий', validators=[Length(
                                                        min=0, max=500,
                                                        message='Поле "Комментарий" не должен превышать 500 знаков.')])
    accomplished = BooleanField('Статус')
    services = SelectMultipleField("Услуги", validate_choice=False)

    def validate_time(self, field):
        start, sunday_finish, finish = time(8, 0), time(16, 0), time(20, 0)
        if not field.data:
            return
        if field.data < start:
            raise ValidationError('Мы начинаем работать с 8:00.')
        if field.data > finish:
            raise ValidationError('С понедельника по субботу мы работаем до 20:00.')
        if self.date.data and self.date.data.isoweekday() == 7 and field.data > sunday_finish:
            raise ValidationError(f'Похоже, что {self.date.data.strftime("%d.%m.%Y")} - это воскресенье. '
                                  f'А по воскресеньям мы работаем до 16:00.')

    def validate_client(self, field):
        clients = [i.phone_number for i in Client.query.all()]
        if field.data not in clients:
            raise ValidationError('Такого клиента пока нет в базе данных.')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from .models import User, Hairdresser, Salon, Service, Type
from .utils import Unique, MyForm, MyDateField, MyFloatField

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
                                      Length(min=0, max=128, message='Поле "Название" не должно превышать 128 знаков.')])
    phone_number = StringField('Номер телефона', validators=[Length(min=0, max=13,
                                                 message='Поле "Номер телефона" не должно '
                                                         'превышать 13 знаков (+375XXXXXXXXX).')])
    latitude = MyFloatField('Широта', validators=[Optional()])
    longitude = MyFloatField('Долгота', validators=[Optional()])


CHOICES=[(row.id, row.name) for row in Type.query.all()]

class ServiceForm(MyForm):
    name = StringField('Название',
                       validators=[DataRequired(message='Обязательное поле.'),
                                   Length(min=0, max=128, message='Поле "Название" не должно превышать 128 знаков.')])
    price = MyFloatField('Цена', validators=[Optional()])
    type = SelectField('Тип', choices=CHOICES)
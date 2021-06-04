from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Optional
from .models import User, Hairdresser
from .utils import MyDateField, Unique

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

class HairdresserForm(FlaskForm):
    name = StringField('Фамилия и имя',
                       validators=[Unique(object_class=Hairdresser, column='name',
                                          message='Мастер с таким именем уже существует.'),
                                   DataRequired(message='Обязательное поле.'),
                                   Length(min=0, max=128, message='Поле "Имя" не должно превышать 128 знаков.')])
    dob = MyDateField('День рождения', validators=[Optional()], format='%d.%m.%Y')
    specialization = TextAreaField('Специализация',
                                   validators=[Length(min=0, max=500,
                                                      message='Поле "Специализация" не должно превышать 500 знаков.')])
    is_available = BooleanField('Статус')
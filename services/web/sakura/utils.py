from wtforms import DateField, FloatField
import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError


class MyForm(FlaskForm):

    def __init__(self, edit=False):
        super(MyForm, self).__init__()
        self.edit = edit


class Unique(object):

    def __init__(self, object_class=None, column=None, message=None):
        if not object_class:
            raise ValueError('Не указан класс объекта.')
        self.object_class = object_class
        if not column:
            column = 'id'
        self.column = column
        if not message:
            message = u'Запись с таким значением уже существует.'
        self.message = message

    def __call__(self, form, field):
        objects = self.object_class.query.all()
        if field.data in [i.__dict__[self.column] for i in objects] and form.edit is False:
            raise ValidationError(self.message)

unique = Unique


class MyDateField(DateField):

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        try:
            self.data = datetime.datetime.strptime(date_str, self.format).date()
        except ValueError:
            self.data = None
            raise ValueError(self.gettext('Введите корректную дату в формате ДД.ММ.ГГГГ.'))


class MyFloatField(FloatField):

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        try:
            self.data = float(valuelist[0])
        except ValueError:
            self.data = None
            raise ValueError(self.gettext('Введите числовое значение с разделителем в виде точки.'))

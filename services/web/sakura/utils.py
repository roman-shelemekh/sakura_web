from flask import abort, request
from wtforms import DateField, FloatField, TimeField
import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
import functools


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
            self.data = datetime.strptime(date_str, self.format).date()
        except ValueError:
            self.data = None
            raise ValueError(self.gettext('Введите корректную дату в формате ДД.ММ.ГГГГ.'))


class MyTimeField(TimeField):

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        time_str = " ".join(valuelist)
        try:
            self.data = datetime.strptime(time_str, self.format).time()
        except ValueError:
            self.data = None
            raise ValueError(self.gettext("Введите корректное время в формате ЧЧ:ММ."))


class MyFloatField(FloatField):

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        try:
            self.data = float(valuelist[0])
        except ValueError:
            self.data = None
            raise ValueError(self.gettext('Введите числовое значение с разделителем в виде точки.'))


month_names = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь',
                       'ноябрь', 'декабрь']


# навигация по графику работы

def months_to_navigate(year, month):
    current_month_start = datetime(date.today().year, date.today().month, 1)
    past_months = list(reversed([(i.year, i.month, month_names[i.month - 1] + ' ' + str(i.year)) for i
                                 in [current_month_start + relativedelta(months=-i-1) for i in range(4)]]))
    coming_months = [(i.year, i.month, month_names[i.month - 1] + ' ' + str(i.year)) for i
                     in [current_month_start + relativedelta(months=+i) for i in range(7)]]
    return  past_months + coming_months

def month_for_heading(year, month):
    return month_names[month-1] + ' ' + str(year)


# навигация по записям

def periods_to_navigate():
    today = datetime.today()
    periods = [('', 'Все'),
               ((today - timedelta(days=1)).strftime('%Y/%m/%d'), 'Вчера'),
               (today.strftime('%Y/%m/%d'), 'Сегодня'),
               ((today + timedelta(days=1)).strftime('%Y/%m/%d'), 'Завтра'),
               (f'?start={today.strftime("%Y-%m-%d")}&end={(today + timedelta(days=7)).strftime("%Y-%m-%d")}', 'В течение недели'),
               (f'?start={today.strftime("%Y-%m-%d")}&end={(today + timedelta(days=30)).strftime("%Y-%m-%d")}', 'В течение месяца')]
    return periods


def is_fetch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return func(*args, **kwargs)
        else:
            abort(403)
    return wrapper

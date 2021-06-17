from . import app
import datetime

@app.template_filter('ru_date')
def format_date(value):
    if isinstance(value, datetime.date):
        value = value.strftime('%d.%m.%Y')
    return value

@app.template_filter('ru_time')
def format_time(value):
    if isinstance(value, datetime.time):
        value = value.strftime('%H:%M')
    return value

@app.template_filter('ru_weekday')
def format_weekday(value):
    weekdays = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    if isinstance(value, datetime.date):
        weekday = weekdays[value.isoweekday()-1]
    return weekday

@app.template_filter('float_round')
def round_float(value):
    if isinstance(value, float):
        value = '{:0.2f}'.format(value)
    return value
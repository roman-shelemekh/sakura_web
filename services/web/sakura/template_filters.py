from . import app
import datetime

@app.template_filter('ru_date')
def format_date(value):
    if isinstance(value, datetime.date):
        value = value.strftime('%d.%m.%Y')
    return value

@app.template_filter('ru_weekday')
def format_date(value):
    weekdays = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    if isinstance(value, datetime.date):
        weekday = weekdays[value.isoweekday()-1]
    return weekday
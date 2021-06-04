from . import app
import datetime

@app.template_filter('ru_date')
def format_date(value):
    if isinstance(value, datetime.date):
        value = value.strftime('%d.%m.%Y')
    return value
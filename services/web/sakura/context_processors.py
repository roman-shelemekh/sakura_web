from . import app
from datetime import datetime


@app.context_processor
def inject_date():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    date = datetime.now().strftime('%d.%m.%Y')
    return dict(current_year=year, current_month=month, current_day=day, current_date=date)
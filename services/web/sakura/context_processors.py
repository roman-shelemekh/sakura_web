from . import app
from datetime import datetime
from .models import Salon


@app.context_processor
def inject_date():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    date = datetime.now().strftime('%d.%m.%Y')
    return dict(current_year=year, current_month=month, current_day=day, current_date=date)

@app.context_processor
def inject_salon():
    try:
        salon_translit = Salon.query.order_by(Salon.id).first().translit
    except:
        salon_translit = None
    return dict(first_salon_translit=salon_translit)
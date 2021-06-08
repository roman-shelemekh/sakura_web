from . import app
from datetime import datetime


@app.context_processor
def inject_year_and_month():
    year = datetime.now().year
    month = datetime.now().month
    return dict(current_year=year, current_month=month)
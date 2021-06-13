from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login
from datetime import datetime
from calendar import monthrange
from sqlalchemy import CheckConstraint


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Salon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    address = db.Column(db.String(128), unique=True, nullable=False)
    phone_number = db.Column(db.String(13))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    translit = db.Column(db.String)
    appointments = db.relationship('Appointment', backref='salon_appointment', lazy=True)
    shifts = db.relationship('Shifts', backref='salon_shifts', lazy=True)
    __table_args__ = (db.UniqueConstraint('latitude', 'longitude'),)

    def __repr__(self):
        return self.name


specialization = db.Table('specialization',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id', ondelete='CASCADE'), primary_key=True),
    db.Column('hairdresser_id', db.Integer, db.ForeignKey('hairdresser.id', ondelete='CASCADE'), primary_key=True)
)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id', ondelete='SET NULL'))

    def __repr__(self):
        return self.name


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    services = db.relationship('Service', backref='service_type', lazy=True)

    def __repr__(self):
        return self.name


class Hairdresser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    comment = db.Column(db.String(500))
    specialization = db.relationship('Service', secondary=specialization, lazy='subquery',
                                     backref=db.backref('service_hairdresser', lazy=True))
    appointments = db.relationship('Appointment', backref='hairdresser_appointment', lazy=True)
    shifts = db.relationship('Shifts', backref='hairdresser_shifts', lazy=True)

    def __repr__(self):
        return self.name


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(13), unique=True, nullable=False)
    discount = db.Column(db.Integer, default=0)
    appointments = db.relationship('Appointment', backref='client_appointment', lazy=True)

    __table_args__ = (CheckConstraint("discount<=100", name='discount_constraint'),)

    def __repr__(self):
        return self.phone_number


service_to_appointment = db.Table('service_to_appointment',
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointment.id', ondelete='CASCADE'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id', ondelete='CASCADE'), primary_key=True)
)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id', ondelete='SET NULL'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='SET NULL'))
    hairdresser_id = db.Column(db.Integer, db.ForeignKey('hairdresser.id', ondelete='SET NULL'))
    comment = db.Column(db.String(500))
    accomplished = db.Column(db.Boolean(), default=True)
    service_to_appointment = db.relationship('Service', secondary=service_to_appointment, lazy='subquery',
                                             backref=db.backref('service_appointment', lazy=True))


class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    shifts = db.relationship('Shifts', backref='calendar_shifts')

    def __repr__(self):
        return self.date.strftime('%d.%m.%Y')

    def month(self, year, month):
        dayn = monthrange(year, month)[-1]
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, dayn)
        dates = self.query.filter(Calendar.date.between(first_day, last_day)).all()
        return dates


class Shifts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_id = db.Column(db.Integer, db.ForeignKey('calendar.id'))
    hairdresser_id = db.Column(db.Integer, db.ForeignKey('hairdresser.id', ondelete='CASCADE'))
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id', ondelete='CASCADE'))
    __table_args__ = (db.UniqueConstraint('date_id', 'hairdresser_id'),)

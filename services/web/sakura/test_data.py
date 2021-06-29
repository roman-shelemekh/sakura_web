from datetime import datetime, timedelta
import random


def create_salons():
    db.session.add_all([
        Salon(name='Сакура на МОПРа', address='ул. МОПРа 5/2', phone_number='+375297913622', translit='sakura_na_mopra'),
        Salon(name='Сакура на Я.Купалы', address='ул. Я.Купалы 10/2', phone_number='+375297912345',
              translit='sakura_na_jakupaly'),
    ])
    db.session.commit()

def create_types():
    db.session.add_all([
        Type(name='мужской зал'),
        Type(name='женский зал'),
        Type(name='маникюр')
    ])
    db.session.commit()

def create_services():
    db.session.add_all([
        Service(name='Стрижка наголо', price='3.99', type_id=1),
        Service(name='Стрижка модельная', price='6.5', type_id=1),
        Service(name='Оформление бороды', price='3.2', type_id=1),
        Service(name='Стрижка полубокс', price='7', type_id=1),
        Service(name='Стрижка челки', price='3', type_id=2),
        Service(name='Стрижка модельная', price='8', type_id=2),
        Service(name='Мелирование волос', price='25', type_id=2),
        Service(name='Окрашивание волос', price='19.9', type_id=2),
        Service(name='Укладка волос', price='14', type_id=2),
        Service(name='Прическа', price='13.5', type_id=2),
        Service(name='Маникюр', price='8.5', type_id=3),
        Service(name='Покрытие ногтей гелем', price='8', type_id=3),
    ])
    db.session.commit()

def create_hairdressers():
    db.session.add_all([
        Hairdresser(name='Наталья Ростова', dob=datetime(1993, 4, 17), is_available=True),
        Hairdresser(name='Елена Курагина', dob=datetime(1995, 1, 23), is_available=True),
        Hairdresser(name='Елизавета Болконская', dob=datetime(1996, 11, 3), is_available=True),
        Hairdresser(name='Софья Мамонтова', dob=datetime(1986, 9, 14), is_available=True),
        Hairdresser(name='Анна Друбецкая', dob=datetime(1989, 3, 8), is_available=False,
                    comment='В декретном отпуске до 05.12.2022'),
        Hairdresser(name='Мария Долохова', dob=datetime(2001, 5, 23), is_available=True),
    ])
    db.session.commit()
    for i in Hairdresser.query.all():
        i.specialization = random.sample(Service.query.all(), random.randint(8, 12))
        db.session.commit()

def create_clients():
    names = ['Михаил', 'Максим', 'Артем', 'Марк', 'Иван',  'Мария', 'Анна', 'Алиса', 'Виктория', 'Полина', 'Стефания',
             'Роберт', 'Оливия', 'Мелания', 'Стефан', 'Теодор']
    db.session.add_all([
        Client(name=random.choice(names), phone_number='+37529' + str(random.randint(5000000, 9999999))) for i in range(50)
    ])
    db.session.commit()


def create_shifts():
    for date in Calendar.query.filter(Calendar.date.between(datetime.now().date() - timedelta(days=30),
                                      datetime.now().date() + timedelta(days=60))).all():
        for hairdresser in random.sample(Hairdresser.query.all(), 2):
            db.session.add(Shifts(date_id=date.id, hairdresser_id=hairdresser.id,
                                 salon_id=Salon.query.order_by(Salon.id).first().id))
            db.session.commit()



def random_date(start, end):
    return (start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))).date()

timetable = [(datetime(2020, 1, 1, 8, 0) + timedelta(minutes=10 * i)).time() for i in range(6*12)]
comments = ['Очень внимательное отношение к гигиене', 'Клиент предпочитает прямые виски',
            'Клиент отказался от мытья головы', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

def create_appointments(qty, start, end, accomplished):
    for i in range(qty):
        date = random_date(start, end)
        time = random.choice(timetable)
        salon_id = Salon.query.order_by(Salon.id).first().id
        client_id = random.choice([i.id for i in Client.query.all()])
        hairdresser_id = random.choice([shift.hairdresser_shifts.id for shift
                        in Shifts.query.filter(Shifts.date_id == Calendar.query.filter(Calendar.date == date).first().id)])
        services = random.sample([service.id for service in Hairdresser.query.get(hairdresser_id).specialization],
                                 random.randint(1,4))
        comment = random.choice(comments)
        app = Appointment(date=date, time=time, salon_id=salon_id, client_id=client_id, hairdresser_id=hairdresser_id,
                          comment=comment, accomplished=accomplished)
        db.session.add(app)
        db.session.commit()
        for service_id in services:
            service = ServiceToAppointment(service_id=service_id, appointment_id=app.id)
            service.set_price()
            db.session.add(service)
            db.session.commit()


create_salons()
create_types()
create_services()
create_hairdressers()
create_clients()
create_shifts()
create_appointments(300, datetime.now() - timedelta(days=30), datetime.now(), True)
create_appointments(30, datetime.now(), datetime.now() + timedelta(days=30), False)

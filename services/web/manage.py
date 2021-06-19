from sakura import app, db

from sakura.models import (
    User, Salon, Service, Hairdresser, Client, Appointment, Calendar, Shifts, Type, ServiceToAppointment
)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Salon': Salon,
        'Service': Service,
        'Hairdresser': Hairdresser,
        'Client': Client,
        'Appointment': Appointment,
        'Calendar': Calendar,
        'Shifts': Shifts,
        'Type': Type,
        'ServiceToAppointment': ServiceToAppointment,
    }
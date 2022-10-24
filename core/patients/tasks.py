from celery import shared_task
import celery
import time
import jdatetime
from patients.models import Patient
from doctors.models import DoctorUser
from patients.models import Appointment


@shared_task
def check_appointment_for_doctor():
    """
    this task ...
    """
    all_doctor = DoctorUser.objects.all()
    for doctor in all_doctor:
        a = Appointment.objects.filter(doctor=doctor).first()
        create_new_appointment = a.doctor_appointments()
        return {'msg': 'check appointments and create new appointment for feture'}


@shared_task
def check_deprecated_appointment():
    """
    convert reserve appointment to reserved after date of appointment (Runs every 24 hours)
    """
    today = jdatetime.datetime.today().date()
    deprecated_appointment = Appointment.objects.filter(
        status_reservation='reserve', date_of_visit__lt=today)
    deprecated_appointment.update(status_reservation='reserved')


@shared_task
def send_sms_to_patient_one_day_to_appointment():
    """
    this task sending SMS to remind patients on the appointment date (Runs every 24 hours)
    """

    all_reserve_appointment = Appointment.objects.filter(
        status_reservation='reserve')
    for appointment in all_reserve_appointment:
        date_of_appointment = appointment.date_of_visit
        today = jdatetime.datetime.today().date()
        delta = (date_of_appointment-today).days
        if delta == 0:
            phone_number_of_patient = appointment.user.phone_number
            patient_name = appointment.user.full_name
            doctor_name = appointment.doctor.full_name
            time_of_appointment = appointment.start_visit_time

            # sms with kave negar
            print(f'sms to {phone_number_of_patient}')
            print(f'{patient_name} aziz nobat pezeshk shoma az doctor {doctor_name}farda da tarikh {str(date_of_appointment)}  dar saat {time_of_appointment} gharar darad lotfan 15 daghighe ghabl dar matab hozor dashte bashid')
        else:
            continue


# import jdatetime
# from datetime import timedelta
# today = jdatetime.datetime.today().date()
# from django.db.models import F, ExpressionWrapper, fields
# duration = ExpressionWrapper(F('date_of_visit') - F(today), output_field=fields.DurationField())
# all_reserve_appointment = Appointment.objects.filter(status_reservation='reserve').annotate(duration=duration).filter(duration=timedelta(days=0))

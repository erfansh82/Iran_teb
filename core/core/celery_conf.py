import time
import django
from celery import Celery,shared_task
from datetime import timedelta
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# redis://redis:6379
BROKER_URL = 'amqp://rabbitmq'

celery_app = Celery('core',broker=BROKER_URL,include=["core.tasks","patients.tasks"])
celery_app.autodiscover_tasks()

celery_app.conf.broker_read_url = 'amqp://rabbitmq'
celery_app.conf.result_backend =  'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['json', 'pickle']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 4



# django.setup()

# BROKER_URL = "amqp://guest:guest@localhost/"

# app = Celery('core', broker=BROKER_URL)

# timezone = 'Asia/Tehran'

# enable_utc = True

# app.config_from_object('django.conf:settings', namespace='CELERY')


# app.conf.beat_schedule = {
# 'add-every-30-seconds': {
# 'task': 'test1',
# 'schedule': 30.0,
# },
# }
# app.conf.timezone = 'UTC'



# @celery_app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
    # Execute daily at midnight...
    # sender.add_periodic_task(
        # crontab(minute=0, hour=0),
        # crontab(),
        # 1,
        # ,
    # )



@shared_task
def a():
    time.sleep(secs=10)
    print('salam be to ')

# from patients.models import Appointment
# from doctors.models import DoctorUser


# def check_appointment_for_doctor():
   # all_doctor=DoctorUser.objects.all()
   # for doctor in all_doctor:
    # a = Appointment.objects.filter(doctor=doctor).first()
    # create_appointment=a.doctor_appointments()
    # return {'msg':'check appointments and create new appointment for feture'}
#
#
# def check_deprecated_appointment():
   # today=jdatetime.datetime.today().date()
   # deprecated_appointment=Appointment.objects.filter(status_reservation='reserve',date_of_visit__lt=today)
   # deprecated_appointment.update(status_reservation='reserved')
#

# def send_sms_to_patient_one_day_to_appointment():
#     all_reserve_appointment = Appointment.objects.filter(
#         status_reservation='reserve')
#     for appointment in all_reserve_appointment:
#         date_of_appointment = appointment.date_of_visit
#         to_day = jdatetime.datetime.today().date()
#         delta = (date_of_appointment-to_day).days
#         if delta == 1:
#             phone_number_of_patient = appointment.user.phone_number
#             patient_name = appointment.user.full_name
#             doctor_name = appointment.doctor.full_name
#             time_of_appointment = appointment.start_visit_time

#             # sms with kave negar
#             print(f'sms to {phone_number_of_patient}')
#             print(f'{patient_name} aziz nobat pezeshk shoma az doctor {doctor_name}farda da tarikh {str(date_of_appointment)}  dar saat {time_of_appointment} gharar darad lotfan 15 daghighe ghabl dar matab hozor dashte bashid')
#         else:
#             continue

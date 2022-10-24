from django.db.models.signals import post_save
from django.dispatch import receiver
from patients.models import Appointment, Patient, Wallet
from kavenegar import *
from core.tasks import send_SMS_task


@receiver(post_save, sender=Patient)
def create_first_obj_appointment(sender, instance, created, **kwargs):
    """
    signal for create wallet for patient after create account
    """
    if created:
        Wallet.objects.create(user=instance)
        return True


@receiver(post_save, sender=Appointment)
def send_sms_for_reserve_appointment_by_patient(sender, instance, created, **kwargs):
    """
    signal for sending SMS to patient after reresve appointment
    """
    if instance.status_reservation == 'reserve' and instance.payment == True:
        phone_number_of_patient = '0'+str(instance.user.phone_number)[2:]
        patient_name = instance.user.full_name
        doctor_name = instance.doctor.full_name
        date_of_appointment = instance.date_of_visit
        time_of_appointment = instance.start_visit_time

        text = f'{patient_name} aziz nobat show az doctor {doctor_name} dar tarikh {str(date_of_appointment)} va saat {time_of_appointment} sabt shod '
        # send sms by kavenegar
        send_SMS_task.delay(phone_number_of_patient, text)
        return True

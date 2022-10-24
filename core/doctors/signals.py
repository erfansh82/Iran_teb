import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from doctors.models import DoctorUser
from patients.models import Appointment, Wallet
from core.tasks import send_SMS_task
from core.sms import send_sms

@receiver(post_save, sender=DoctorUser)
def create_first_obj_appointment(sender, instance, created, **kwargs):
    if created:
        Appointment.objects.create(doctor=instance)
        return True


@receiver(post_save, sender=Appointment)
def send_sms_for_cancel_appointment_by_docotor(sender, instance, created, **kwargs):
    if instance.status_reservation == 'cancel':
        phone_number_of_patient = instance.user.phone_number
        patient_name = instance.user.full_name
        doctor_name = instance.doctor.full_name
        date_of_appointment = instance.date_of_visit
        time_of_appointment = instance.start_visit_time
        
        text=f'{patient_name} aziz nobat pezeshk show dar tarikh {str(date_of_appointment)} va saat {time_of_appointment} tavasot doctor{doctor_name} be dalil moshkel kari calcel shod '
        # send sms by kavenegar
        send_SMS_task.delay(phone_number_of_patient,text)
        # send_sms(phone_number_of_patient,text)

        if instance.payment == True:
            cost_of_visit_doctor = instance.doctor.cost_of_visit
            patient_user = instance.user
            patient_wallet=Wallet.objects.get(user=patient_user)
            patient_wallet.wallet_balance=cost_of_visit_doctor
            patient_wallet.save()
            instance.payment=False
            instance.save()
            print('pardakht shod###########################')

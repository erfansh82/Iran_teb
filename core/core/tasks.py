from celery import shared_task
import time
from core.sms import send_sms



@shared_task
def send_SMS_task(phone_number,text):
    return send_sms(phone_number,text)
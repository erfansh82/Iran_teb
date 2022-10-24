import random
import redis
from datetime import timedelta
import jdatetime
import requests
import json

from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.shortcuts import render
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from patients.models import Patient, Wallet, Appointment
from doctors.models import DoctorUser, CommentForDoctor
from core.tasks import send_SMS_task

from patients.serializers import (ReserveAppointmentSerializer, MyDoctorsSerializer,
                                  DoctorFreeAppointmentSerializer, RserveAppointmentByPatientSerializer,
                                  WalletSerializer, patientCompleteInfoSerilizer, LogOutSerializer, AddCommentSerializers)


r = redis.Redis(host='localhost', port=6379, db=0)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Customizing JWt token claims
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['phone_number'] = user.phone_number
        token['full_name'] = user.full_name
        token['who'] = user.doctor_or_patient

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


def get_tokens_for_user(user):
    refresh = MyTokenObtainPairSerializer.get_token(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class GetUserInfoAndId(APIView):
    """
     helping api for front end about user info
    """

    def post(self, request):
        data = self.request.data
        access_token = data['access_token']
        access_token_obj = AccessToken(access_token)
        user_id = access_token_obj['user_id']
        user_full_name = access_token_obj['full_name']
        user_phone_number = access_token_obj['phone_number']
        who = access_token_obj['who']
        return Response({'user_id': user_id, 'user_full_name': user_full_name, 'who': who, 'user_phone_number': user_phone_number})


class PatientLoginSendOTp(APIView):
    """
    api for patient login
    """
    def post(self, request):
        phone_number = self.request.data['phone_number']
        if not phone_number:
            return Response({"msg": "phone number is requierd'"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            dr_user = Patient.objects.get(phone_number=phone_number)
        except:
            return Response({"msg": "you dont have any user account with this phone number please register "}, status=status.HTTP_400_BAD_REQUEST)

        code = random.randint(10000, 99999)

        r.setex(str(phone_number), timedelta(minutes=2), value=code)
        send_SMS_task.delay(phone_number, code)
        print('*****************************')
        print(r.get(str(phone_number)).decode())

        return Response({"msg": "code sent successfully"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    api for logout patient
    """
    def post(self, request, *args):
        serializer = LogOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientRegisterSendOTp (APIView):
    """
    api for patient register
    """

    def post(self, request):
        phone_number = self.request.data['phone_number']
        if not phone_number:
            return Response({"msg": "phone number is requierd'"}, status=status.HTTP_400_BAD_REQUEST)

        patient = Patient.objects.create(
            phone_number=phone_number, is_active=False, doctor_or_patient='patient')

        code = random.randint(10000, 99999)
        r.setex(str(phone_number), timedelta(minutes=2), value=code)
        send_SMS_task.delay(phone_number, code)
        print('*****************************')
        print(r.get(str(phone_number)).decode())

        return Response({"msg": "code sent successfully"}, status=status.HTTP_200_OK)


class PatientVerifyOTP(APIView):
    """
    api for check OTp code for login patient
    """

    def post(self, request):
        phone_number = self.request.data['phone_number']
        patient = Patient.objects.get(phone_number=phone_number)
        code = self.request.data['code']
        cached_code = r.get(str(phone_number)).decode()
        if code != cached_code:
            return Response({"msg": "code not matched"}, status=status.HTTP_403_FORBIDDEN)
        token = get_tokens_for_user(patient)
        return Response(token, status=status.HTTP_201_CREATED)


class PatientCompleteInfo(APIView):
    """
    api for complete patient info after registeration
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = self.request.data
        phone_number = data['phone_number']

        patient = Patient.objects.get(phone_number=phone_number)
        serializer = patientCompleteInfoSerilizer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            patient.is_active = True
            patient.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NumActiveUser(APIView):
    """
    api for number of active patient in website
    """

    def get(self, request):
        query = Patient.objects.filter(is_active=True).count()
        return Response({"num_active_user": query}, status=status.HTTP_200_OK)


class NumSuccessfulReseced(APIView):
    """
    api for number of success reserve Appointment
    """

    def get(self, request):
        query = Appointment.objects.filter(
            status_reservation='reserved').count()
        return Response({"num_success_reserved": query}, status=status.HTTP_200_OK)


class UserSatisfy(APIView):
    """
    api for average rate of all doctor
    """

    def get(self, request):
        query = CommentForDoctor.objects.all().aggregate(Avg('rating'))
        a = f" {query['rating__avg']*20} % "
        return Response({"percent_satisfy": a}, status=status.HTTP_200_OK)


class AddCommentForOneDoctor(APIView):
    """
    api for add comment for doctor (only patients who have been visited by doctors can add comment)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, dr_id):
        user_instance = Patient.objects.get(id=request.user.id)
        doctor_instance = DoctorUser.objects.get(id=dr_id)
        context = {
            'doctor': doctor_instance,
            'user': user_instance,
            'desciption': request.data['desciption'],
            'rating': request.data['rating']
        }
        serializer = AddCommentSerializers(data=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientReserveAppointments(APIView):
    """
    list of all reserve appointments for specific patient
    """
    permission_classes = [IsAuthenticated]

    def get(self, request,):
        pra_query = Appointment.objects.filter(
            user__id=request.user.id, status_reservation='reserve')
        serializer = ReserveAppointmentSerializer(pra_query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientReservedAppointments(APIView):
    """
    list of all reserved appointments for specific patient
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pra_query = Appointment.objects.filter(
            user__id=request.user.id, status_reservation='reserved')
        serializer = ReserveAppointmentSerializer(pra_query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyDoctor(APIView):
    """
    list of all the doctors that the patient has had appointments 
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        l = ['reserve', 'reserved', 'cancel']
        ra_query = Appointment.objects.filter(
            user__id=request.user.id, status_reservation__in=l)
        serializer = MyDoctorsSerializer(
            ra_query, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK,)


class DoctorFreeAppointment(APIView):
    """
    list of all free appointments of a doctor that a patient can reserve appointment  
    """

    def get(self, request, dr_id):
        query = Appointment.objects.filter(
            doctor__id=dr_id, status_reservation='free')
        serializer = DoctorFreeAppointmentSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK,)


class MyWallet(APIView):
    """
    patient's wallet, which will be returned to the wallet if the appointment is canceled
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = Wallet.objects.get(user__id=request.user.id)
        serializer = WalletSerializer(query)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RservingAppointmentByPatient(APIView):
    """
    api for reserving doctor apointment by patient
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, dr_id):
        user_instance = Patient.objects.get(id=request.user.id)
        data = self.request.data
        start_visit_time = data['start_visit_time']
        end_visit_time = data['end_visit_time']
        date_of_visit = data['date_of_visit']
        q = Appointment.objects.filter(
            doctor__id=dr_id, start_visit_time=start_visit_time, end_visit_time=end_visit_time,
            date_of_visit=date_of_visit, status_reservation='free').first()
        q.user = user_instance
        q.status_reservation = 'reserve'
        q.reservetion_code = random.randint(10000, 99999)
        q.save()
        serializer = RserveAppointmentByPatientSerializer(q)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CancelAppointmentByPatient(APIView):
    """
    api for cancel doctor appointment by patient 48hr before appointment date 
     (The cost of the visit will be returned to the patient wallet after cancellation)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, dr_id):
        data = self.request.data
        start_visit_time = data['start_visit_time']
        end_visit_time = data['end_visit_time']
        date_of_visit = data['date_of_visit']
        reserve_appointment = Appointment.objects.filter(
            user__id=request.user.id, doctor__id=dr_id, date_of_visit=date_of_visit, start_visit_time=start_visit_time,
            end_visit_time=end_visit_time, status_reservation='reserve').first()

        date_of_appointment = reserve_appointment.date_of_visit
        to_day = jdatetime.datetime.today().date()
        delta = (date_of_appointment-to_day).days
        if delta >= 2:
            if reserve_appointment.payment == True:
                cost_of_visit_doctor = reserve_appointment.doctor.cost_of_visit
                patient_user = reserve_appointment.user
                patient_wallet = Wallet.objects.get(user=patient_user)
                patient_wallet.wallet_balance = cost_of_visit_doctor
                patient_wallet.save()
                reserve_appointment.payment = False
                reserve_appointment.save()

            reserve_appointment.user = None
            reserve_appointment.reservetion_code = None
            reserve_appointment.status_reservation = 'free'
            reserve_appointment.save()

            return Response({'msg': 'appointment canceled by patient'}, status=status.HTTP_200_OK)

        return Response({'msg': 'you can cancel appointment minimomon 48hour befor resserve time '}, status=status.HTTP_400_BAD_REQUEST)


class CnacelAppointmentByDoctor(APIView):
    """
    api for cancel doctor appointment by doctor 48hr before appointment date 
     (The cost of the visit will be returned to the patient wallet after cancellation)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, u_id, dr_id):
        data = self.request.data
        start_visit_time = data['start_visit_time']
        end_visit_time = data['end_visit_time']
        date_of_visit = data['date_of_visit']
        reserve_appointment = Appointment.objects.filter(
            user__id=u_id, doctor__id=dr_id, date_of_visit=date_of_visit, start_visit_time=start_visit_time,
            end_visit_time=end_visit_time, status_reservation='reserve').first()

        date_of_appointment = reserve_appointment.date_of_visit
        to_day = jdatetime.datetime.today().date()
        delta = (date_of_appointment-to_day).days
        if delta >= 2:
            reserve_appointment.status_reservation = 'cancel'
            reserve_appointment.save()
            return Response({'msg': 'appointment canceled by doctor'}, status=status.HTTP_200_OK)

        return Response({'msg': 'you can cancel maximon 48hour befor resserve time '}, status=status.HTTP_400_BAD_REQUEST)


MERCHANT = ''
ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/{authority}"
amount = 10000  # Rial / Required
description = "پرداخت هزینه ویزیت"  # Required
email = ''  # Optional
mobile = ''  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://localhost:8000/verify-payment/'


class request_payment(APIView):
    """
    zarin pal bank gateway to pay cost of doctors visit
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # print(self.request.user.id)
        appointment = Appointment.objects.filter(
            user__id=self.request.user.id, status_reservation='reserve', payment=False).first()
        r.setex(str(appointment.user.phone_number),
                timedelta(minutes=5), value=appointment.id)
        amount = appointment.get_total_price()
        req_data = {
            "merchant_id": MERCHANT,
            "amount": 10000,
            "callback_url": CallbackURL,
            "description": description,
            "metadata": {"mobile": appointment.user.phone_number}
        }
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        authority = req.json()['data']['authority']
        print(
            '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        if len(req.json()['errors']) == 0:
            return HttpResponseRedirect(ZP_API_STARTPAY.format(authority=authority))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


class verify_payment(APIView):
    def get(self, request):
        appointment_id = r.get(str(self.request.user.phone_number)).decode()
        appointment = Appointment.objects.get(id=int(appointment_id))
        amount = appointment.get_total_price()
        t_status = request.GET.get('Status')
        t_authority = request.GET['Authority']
        if request.GET.get('Status') == 'OK':
            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            req_data = {
                "merchant_id": MERCHANT,
                "amount": amount,
                "authority": t_authority
            }
            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(
                req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']
                if t_status == 100:
                    appointment.payment = True
                    appointment.payment_code = int(
                        req.json()['data']['ref_id'])
                    appointment.save()
                    return HttpResponse('Transaction success.\nRefID: ' + str(
                        req.json()['data']['ref_id']
                    ))
                elif t_status == 101:
                    return HttpResponse('Transaction submitted : ' + str(
                        req.json()['data']['message']
                    ))
                else:
                    return HttpResponse('Transaction failed.\nStatus: ' + str(
                        req.json()['data']['message']
                    ))
            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")

        else:
            return HttpResponse('Transaction failed or canceled by user')

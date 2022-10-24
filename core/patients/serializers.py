from dataclasses import fields
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from patients.models import Appointment, Wallet, Patient
from doctors.models import CommentForDoctor


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class patientCompleteInfoSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('full_name', 'national_code', 'Insurance',)


class AddCommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = CommentForDoctor
        fields = ('desciption', 'rating','doctor','user')

    def validate(self, data):
        # Only patients who have been visited by doctors can add comment
        doctor=data['doctor']
        user=data['user']
        check_appointmnt=Appointment.objects.filter(doctor=doctor,user=user,status_reservation='reserved').exists()
        if check_appointmnt==False:
            raise serializers.ValidationError("You are not allowed to add comment")
        return data

class ReserveAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('doctor_name', 'reservetion_code', 'doctor_address', 'doctor_telephones',
                  'start_visit_time', 'end_visit_time', 'status_reservation', 'visit_day', 'payment')



class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('user', 'wallet_balance')


class MyDoctorsSerializer(serializers.ModelSerializer):
    doctor = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='doctor:doctor-detail'
    )

    class Meta:
        model = Appointment
        fields = ('doctor_name', 'doctor',)


class DoctorFreeAppointmentSerializer(serializers.ModelSerializer):
    def get_doctor(self, obj):
        return {'doctor_id': obj.doctor.id, 'doctor_name': obj.doctor.full_name}

    def get_day_name(self, obj):
        return obj.date_of_visit.strftime("%A")

    day_name = serializers.SerializerMethodField('get_day_name')

    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = Appointment
        fields = ('doctor', 'start_visit_time',
                  'end_visit_time', 'day_name', 'date_of_visit')


class RserveAppointmentByPatientSerializer(serializers.ModelSerializer):
    def get_doctor(self, obj):
        a = {'full_name': obj.doctor.full_name, 'id': obj.doctor.id}
        return a

    def get_user(self, obj):
        b = {'full_name': obj.user.full_name, 'id': obj.user.id}
        return b

    doctor = serializers.SerializerMethodField('get_doctor')
    user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = Appointment
        fields = ('doctor', 'user', 'start_visit_time',
                  'end_visit_time', 'date_of_visit',)

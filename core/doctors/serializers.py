from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import CommentForDoctor, DoctorUser, Telephone, DoctorCity, DoctorAddress, WeekDays
from .models import DoctorCity, DoctorSpecialist, DoctorShift
from patients.models import Appointment


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


class TopDoctorSerializers(serializers.ModelSerializer):
    class Meta:
        model = DoctorUser
        fields = ('full_name', 'doctor_specialist',
                  'rate', 'experience_years',)


class DoctorSpecialistSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorSpecialist
        fields = '__all__'


class DoctorCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorCity
        fields = ('parent', 'city',)


class AllDoctorSerializers(serializers.ModelSerializer):
    doctor_specilist = DoctorSpecialistSerializer()
    city = DoctorCitySerializer()

    class Meta:
        model = DoctorUser
        fields = ('full_name', 'doctor_specialist', 'rate',
                  'all_patients_reserved', 'experience_years', 'gender', 'city')

# class TelephoneSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Telephone
#         fields='__all__'


class DoctorDetailSerializer(serializers.ModelSerializer):
    city = DoctorCitySerializer()

    doctor_specialist = serializers.SerializerMethodField(
        'get_doctor_specialist', read_only=True)

    def get_doctor_specialist(self, obj):
        a = {"specialist": obj.doctor_specialist.parent,
             " high specialist'": obj.doctor_specialist.specialist}

        return str(a)

    class Meta:
        model = DoctorUser
        fields = ('full_name', 'doctor_specialist', 'rate', 'all_patients_reserved', 'experience_years', 'gender',
                  'city', 'registeration_date', 'doctor_address', 'doctor_telephone', 'work_day', 'user_shifts')


class CommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = CommentForDoctor
        fields = '__all__'


class DoctorReserveApointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('status_reservation', 'patient_name',
                  'patient_phone_number', 'patient_insurance',)


class DrRegisterInformationsserrializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorUser
        fields = ('registeration_date', 'phone_number')


class DoctorTellphoneSerializer(serializers.ModelSerializer):
    def get_doctor(self, obj):
        return obj.doctor.full_name

    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = Telephone
        fields = '__all__'


class DoctorAddressSerializer(serializers.ModelSerializer):
    def get_doctor(self, obj):
        return obj.doctor.full_name

    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = DoctorAddress
        fields = '__all__'


class DrCompleteInfoSerilizer(serializers.ModelSerializer):
    class Meta:
        model = DoctorUser
        fields = ('full_name', 'medical_system_code',
                  'dr_specialist', 'doctor_telephone', 'doctor_address')


class RetriveDrShiftTimeSerializer(serializers.ModelSerializer):
    def get_doctor(self, obj):
        return obj.doctor.full_name

    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = DoctorShift
        fields = '__all__'


class CreateDrShiftTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorShift
        fields = ('start_time', 'end_time')


class DoctorAddressSerilizer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAddress
        fields = ('address', 'lat', 'long')


class RetriveDoctorTellePhoneSerilizer(serializers.ModelSerializer):
    def get_doctor(self, obj):
        return obj.doctor.full_name
    doctor = serializers.SerializerMethodField('get_doctor')

    class Meta:
        model = Telephone
        fields = '__all__'


class CreateDoctorTellePhoneSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Telephone
        fields = ('telephone_number',)


class DoctorVisitTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorUser
        fields = ('visit_time',)


class DoctorWorkDaysSrializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDays
        fields = ('day',)

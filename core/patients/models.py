import datetime as dt
from random import random

from django.db import models
from django_jalali.db import models as jmodels
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, send_mail

from patients.validators import national_code_validator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone_number, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number,
                          username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)

        if not extra_fields.get('no_password'):
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, username=None, phone_number=None, email=None, password=None, **extra_fields):
        if username is None:
            if email:
                username = email.split('@', 1)[0]
            if phone_number:
                username = random.choice(
                    'abcdefghijklmnopqrstuvwxyz') + str(phone_number)[-7:]
            while User.objects.filter(username=username).exists():
                username += str(random.randint(10, 99))

        return self._create_user(username, phone_number, email, password, False, False, **extra_fields)

    def create_superuser(self, username, phone_number, email, password, **extra_fields):
        return self._create_user(username, phone_number, email, password, True, True, **extra_fields)

    def get_by_phone_number(self, phone_number):
        return self.get(**{'phone_number': phone_number})


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username, password and email are required. Other fields are optional.
    """
    choise_user = (('doctor', 'doctor'), ('patient', 'patient'))
    doctor_or_patient = models.CharField(
        choices=choise_user, max_length=10, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True)
    username = models.CharField(('username'), max_length=32, unique=True, null=True, blank=True,
                                help_text=(
                                    'Required. 30 characters or fewer starting with a letter. Letters, digits and underscore only.'),
                                validators=[
                                    validators.RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_\.]+$',
                                                              ('Enter a valid username starting with a-z. '
                                                               'This value may contain only letters, numbers '
                                                               'and underscore characters.'), 'invalid'),
    ],
        error_messages={
                                    'unique': ("A user with that username already exists."),
    }
    )
    full_name = models.CharField(('full name'), max_length=80)
    # national_code = models.PositiveBigIntegerField(null=True)
    # gender_choice = (
    # ('male', 'male'),
    # ('female', 'female'),
    # )
    # gender = models.CharField(choices=gender_choice,
    #   max_length=10, null=True, blank=True)

    email = models.EmailField(
        ('email address'), unique=True, null=True, blank=True)
    phone_number = models.BigIntegerField(('mobile number'), unique=True, null=True, blank=True,
                                          validators=[
                                              validators.RegexValidator(r'^989[0-3,9]\d{8}$',
                                                                        ('Enter a valid mobile number.'), 'invalid'),
    ],
        error_messages={
                                              'unique': ("A user with this mobile number already exists."),
    }
    )
    is_staff = models.BooleanField(('staff status'), default=False,
                                   help_text=('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(('active'), default=True,
                                    help_text=('Designates whether this user should be treated as active. '
                                               'Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)
    last_seen = models.DateTimeField(('last seen date'), null=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'username']

    class Meta:
        db_table = 'users'
        verbose_name = ('user')
        verbose_name_plural = ('users')


    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def ph_number(self):
        return str(self.phone_number)

    @property
    def is_loggedin_user(self):
        """
        Returns True if user has actually logged in with valid credentials.
        """
        return self.phone_number is not None or self.email is not None

    def save(self, *args, **kwargs):
        if self.email is not None and self.email.strip() == '':
            self.email = None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{str(self.phone_number)} - {self.full_name} - {self.doctor_or_patient}'


class Patient(User):
    Insurance_choice = (
        ("اتیه سازان", "atiye sazan"),
        ("تامین اجتماعی", "tamin ejtemayi"),
        ("سامان", "saman"),
        ("دانا", "dana"),
        ("ایران", "iran"),
        ("هیچ کدام", "none"),
    
    )
    gender_choice = (
        ('male', 'male'),
        ('female', 'female'),
    )
# full name and nationa; code registeration_date  gender pak shavad dakhel user asli beravad
    # full_name = models.CharField(max_length=80)
    national_code = models.CharField(max_length=10,
                                     null=True, validators=[national_code_validator])
    registeration_date = jmodels.jDateTimeField(
        auto_now_add=True, null=True, blank=True)
    gender = models.CharField(choices=gender_choice,
                              max_length=10, null=True, blank=True)
    Insurance = models.CharField(max_length=35, choices=Insurance_choice)


class Wallet(models.Model):
    user = models.OneToOneField("patients.Patient", on_delete=models.CASCADE)
    wallet_balance = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f'{self.user}-{self.wallet_balance}'


class Appointment(models.Model):
    STATUS_CHOICE = (
        ("cancel", "cancel"),
        ("reserve", "reserve"),
        ("reserved", "reserved"),
        ("free", "free"),
    )
    doctor = models.ForeignKey(
        "doctors.DoctorUser", on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        "patients.Patient", null=True, blank=True, on_delete=models.DO_NOTHING)
    start_visit_time = models.TimeField(null=True, blank=True)
    end_visit_time = models.TimeField(null=True, blank=True)
    date_of_visit = jmodels.jDateField(null=True, blank=True)
    # day=models.ForeignKey("doctors.WeekDays",on_delete=models.CASCADE,null=True)
    payment = models.BooleanField(default=False)
    payment_code = models.PositiveIntegerField(null=True, blank=True)
    status_reservation = models.CharField(
        choices=STATUS_CHOICE, max_length=27, null=True, blank=True)
    reservetion_code = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f' {self.status_reservation}-for user  {self.user}- from doctor  {self.doctor.full_name}'

# from patients.models import Appointment
#  d = Appointment.objects.filter(status_reservation='reserve')[0]

    def doctor_appointments(self):
        shifts = self.doctor.dr_shift_times
        dr_work_days = self.doctor.dr_work_days
        for date in dr_work_days:
            for shift_time in shifts:
                for visit_time in shift_time:
                    start_visit = visit_time[0]
                    end_visit = visit_time[1]
                    obj = Appointment.objects.filter(doctor=self.doctor, start_visit_time=start_visit,
                                                     end_visit_time=end_visit, date_of_visit=date,).exists()
                    if obj == False:
                        Appointment.objects.create(doctor=self.doctor, start_visit_time=start_visit,
                                                   end_visit_time=end_visit, date_of_visit=date, status_reservation='free'
                                                   )

        return 'doctor appointments create'

    def get_total_price(self):

        return int(self.doctor.cost_of_visit)

    @property
    def visit_day(self):
        d = self.day.day
        return d

    @property
    def patient_name(self):
        n = self.user.full_name
        return n

    @property
    def patient_insurance(self):
        pi = self.user.Insurance
        return pi

    @property
    def patient_phone_number(self):
        pn = self.user.phone_number
        return pn

    @property
    def doctor_name(self):
        n = self.doctor.full_name
        return n

    @property
    def doctor_address(self):
        a = self.doctor.doctor_address
        return a

    @property
    def doctor_telephones(self):
        t = self.doctor.doctor_telephone
        return t

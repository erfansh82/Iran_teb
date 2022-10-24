from django.contrib import admin


from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from doctors.forms import UserAdminCreationForm, UserAdminChangeForm

from patients.models import (
    User as I,
    Patient,
    Wallet,
    Appointment,
)

User = get_user_model()

admin.site.register(I)
admin.site.register(Wallet)
admin.site.register(Appointment)

# Register your models here.


class PatientAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ['id', 'full_name', 'email', 'phone_number', 'national_code',
                    'doctor_or_patient', 'is_active', 'registeration_date', 'Insurance']

    list_filter = ['is_staff']
    fieldsets = (
        (None, {'fields': ('profile_image','full_name', 'phone_number', 'national_code',
         'doctor_or_patient', 'gender', 'Insurance', )}),
        # ('Personal info', {'fields': ('phone_number', 'bio', 'profile_image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'last_seen', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password', 'password_2',)}
         ),
    )
    search_fields = ['full_name', ]
    ordering = ['id']
    filter_horizontal = ()


admin.site.register(Patient, PatientAdmin)

from django.urls import path
from patients import views

# from azbankgateways.urls import az_bank_gateways_urls


urlpatterns = [
    path('get-user-info-and-id/',views.GetUserInfoAndId.as_view()),
    path('patient-register-send-otp/',views.PatientRegisterSendOTp.as_view()),
    path('patient-login-send-otp/',views.PatientLoginSendOTp.as_view()),
    path('patient-verify-otp/',views.PatientVerifyOTP.as_view()),
    path('Logout/',views.LogoutView.as_view()),
    path('patient-complete-info/',views.PatientCompleteInfo.as_view()),
    path('num-active-user/',views.NumActiveUser.as_view()),
    path('num-success-reserved/',views.NumSuccessfulReseced.as_view()),
    path('percent-satisfy/',views.UserSatisfy.as_view()),
    path('add-comment-for-one-doctor/<int:dr_id>/',views.AddCommentForOneDoctor.as_view()),
    path('patient-reserve-appointment/',views.PatientReserveAppointments.as_view()),
    path('patient-reserved-appointment/',views.PatientReservedAppointments.as_view()),
    path('my-wallet/',views.MyWallet.as_view()),
    path('my-doctor/',views.MyDoctor.as_view()),
    path('doctor-free-appointment/<int:dr_id>/',views.DoctorFreeAppointment.as_view()),
    path('rserving-appointment-by-patient/<int:dr_id>/',views.RservingAppointmentByPatient.as_view()),
    path('cancel-appointment-by-patient/<int:dr_id>/',views.CancelAppointmentByPatient.as_view()),
    path('request-payment/', views.request_payment.as_view(), name='request-payment'),
    path('verify-payment/', views.verify_payment.as_view() , name='verify-payment'),

]

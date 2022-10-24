from django.urls import path,include
from doctors import views

app_name='doctor'

urlpatterns = [
    path('active-doctor-user',views.NumActiveDoctor.as_view()),
    path('recent-comment',views.RecentComment.as_view()),
    path('comment-for-doctor/<int:dr_id>',views.CommentForOneDoctor.as_view()),
    path('top-doctors',views.TopDoctors.as_view()),
    path('all-specialist/',views.All_Specialist.as_view()),
    path('doctors-list/',views.DoctorsList.as_view()),
    path('doctor-detail/<int:pk>',views.DoctorDetail.as_view(),name='doctor-detail'),
    path('doctor-advance-search/',views.DoctorAdvanceSearch.as_view()),
    path('doctor-reserve-apointment/<int:pk>',views.DoctorReserveApointment.as_view()),
    path('dr-register-informations/<int:pk>',views.DrRegisterInformations.as_view()),
    path('doctor-register-send-otp/',views.DoctorRegisterSendOTp.as_view()),
    path('doctor-login-send-otp/',views.DoctorLoginSendOTp.as_view()),
    path('dr-verify-otp/',views.DrVerifyOTP.as_view()),
    path('Logout/',views.LogoutView.as_view()),
    path('doctor-complete-info/',views.DrCompleteInfo.as_view()),
    path('retrive-doctor-shift-time/<int:dr_pk>/',views.RetriveDoctorShiftTime.as_view()),
    path('create-doctor-shift-time/<int:dr_pk>/',views.CreateDoctorShiftTime.as_view()),
    path('update-doctor-shift-time/<int:pk>/',views.UpdateDoctorShiftTime.as_view()),
    path('delete-doctor-shift-time/<int:pk>/',views.DeleteDoctorShiftTime.as_view()),
    path('doctor-address/<int:dr_pk>/',views.DoctorAddressInfo.as_view()),
    path('retrive-doctor-tellePhone/<int:dr_pk>/',views.RetriveDoctorTellePhone.as_view()),
    path('create-doctor-tellePhone/<int:dr_pk>/',views.CreateDoctorTellePhone.as_view()),
    path('update-doctor-tellePhone/<int:pk>/',views.UpdateDoctorTellePhone.as_view()),
    path('delete-doctor-tellePhone/<int:pk>/',views.DeleteDoctorTellePhone.as_view()),
    path('doctor-visit-time/<int:dr_pk>/',views.DoctorVisitTime.as_view()),
    path('doctor-work-days/<int:dr_pk>/',views.DoctorWorkDays.as_view()),
    path('doctor-change-phone-number/<int:dr_pk>/',views.DrChangePhoneNumber.as_view()),
    


]
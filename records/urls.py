from django.urls import path
from .views.doctor_views import doctor_queue, booking_requests, appointment_diagnosis, doctor_schedule, doctor_profile, doctor_monthly_planner
from .views.receptionist_views import receptionist_queue, appointment_management, receptionist_profile
from .views.patient_views import patient_consultation_summary

urlpatterns = [
    path('doctor/queue/', doctor_queue, name='doctor_queue'),
    path('doctor/requests/', booking_requests, name='booking_requests'),
    path('doctor/appointment/<int:appointment_id>/diagnosis/', appointment_diagnosis, name='appointment_diagnosis'),
    path('doctor/schedule/', doctor_schedule, name='doctor_schedule'),
    path('doctor/profile/', doctor_profile, name='doctor_profile'),
    path('doctor/month-planner/', doctor_monthly_planner, name='doctor_monthly_planner'),

    path('receptionist/queue/', receptionist_queue, name='receptionist_queue'),
    path('receptionist/management/', appointment_management, name='receptionist_management'),
    path('receptionist/profile/', receptionist_profile, name='receptionist_profile'),

    path('patient/consultation/<int:appointment_id>/', patient_consultation_summary, name='patient_consultation_summary'),
]
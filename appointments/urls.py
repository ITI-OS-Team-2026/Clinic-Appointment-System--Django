from django.urls import path
from .views.patient_views import patient_dashboard, patient_book_appointment, cancel_appointment, patient_reschedule_appointment
from .views.schedule_views import TodayAppointmentsView
from .views.booking_views import (
    ConfirmAppointmentView, CheckInAppointmentView, 
    RescheduleAppointmentView, BookAppointmentAPIView,
    CompleteAppointmentView, NoShowAppointmentView
)
from .views.api_views import DoctorListAPIView, AppointmentSearchView

urlpatterns = [
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    path('patient/book/', patient_book_appointment, name='patient-book-appointment'),
    path('patient/<int:appointment_id>/cancel/', cancel_appointment, name='cancel-appointment'),
    path('patient/<int:appointment_id>/reschedule/', patient_reschedule_appointment, name='patient-reschedule-appointment'),
    
    path('api/doctors/', DoctorListAPIView.as_view(), name='api-doctors-list'),
    path('api/book/', BookAppointmentAPIView.as_view(), name='api-book-appointment'),
    path('api/search/', AppointmentSearchView.as_view(), name='api-appointment-search'),
    
    path('today/', TodayAppointmentsView.as_view(), name='today-appointments'),
    path('<int:appointment_id>/confirm/', ConfirmAppointmentView.as_view(), name='confirm-appointment'),
    path('<int:appointment_id>/checkin/', CheckInAppointmentView.as_view(), name='checkin-appointment'),
    path('<int:appointment_id>/reschedule/', RescheduleAppointmentView.as_view(), name='reschedule-appointment'),
    path('<int:appointment_id>/complete/', CompleteAppointmentView.as_view(), name='complete-appointment'),
    path('<int:appointment_id>/noshow/', NoShowAppointmentView.as_view(), name='noshow-appointment'),
]
from django.urls import path
from .views.patient_views import patient_dashboard
from .views.schedule_views import TodayAppointmentsView
from .views.booking_views import ConfirmAppointmentView, CheckInAppointmentView, RescheduleAppointmentView

urlpatterns = [
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    path('today/', TodayAppointmentsView.as_view(), name='today-appointments'),
    path('<int:appointment_id>/confirm/', ConfirmAppointmentView.as_view(), name='confirm-appointment'),
    path('<int:appointment_id>/checkin/', CheckInAppointmentView.as_view(), name='checkin-appointment'),
    path('<int:appointment_id>/reschedule/', RescheduleAppointmentView.as_view(), name='reschedule-appointment'),
]
from django.urls import path
from .views.doctor_views import doctor_queue
from .views.receptionist_views import receptionist_queue, appointment_management

urlpatterns = [
    path('doctor/queue/', doctor_queue, name='doctor_queue'),
    path('receptionist/queue/', receptionist_queue, name='receptionist_queue'),
    path('receptionist/management/', appointment_management, name='receptionist_management'),
]
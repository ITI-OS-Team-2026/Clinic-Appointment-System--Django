from django.urls import path
from .views.doctor_views import doctor_queue
from .views.receptionist_views import receptionist_queue

urlpatterns = [
    path('doctor/queue/', doctor_queue, name='doctor_queue'),
    path('receptionist/queue/', receptionist_queue, name='receptionist_queue'),
    # path('receptionist/checkin/<int:appointment_id>/', check_in_patient, name='check_in_patient'),
]
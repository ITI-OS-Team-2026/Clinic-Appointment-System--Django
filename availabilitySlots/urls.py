from django.urls import path
from .views import DoctorAvailableSlotsView

urlpatterns = [
    path('doctors/<int:doctor_id>/slots/', DoctorAvailableSlotsView.as_view(), name='doctor-slots'),
]
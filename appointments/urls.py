from django.urls import path
from .views.patient_views import patient_dashboard

urlpatterns = [
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
]
from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'appointment_date', 'start_time', 'end_time', 'status', 'check_in_time']
        read_only_fields = ['id', 'check_in_time']

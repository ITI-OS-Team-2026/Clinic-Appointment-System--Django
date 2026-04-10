from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'patient_name', 'doctor_name', 'appointment_date', 'start_time', 'end_time', 'status', 'check_in_time']
        read_only_fields = ['id', 'check_in_time']
        
    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def get_doctor_name(self, obj):
        return obj.doctor.get_full_name() or obj.doctor.username

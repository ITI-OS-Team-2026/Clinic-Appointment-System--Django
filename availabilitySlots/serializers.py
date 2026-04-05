from rest_framework import serializers
from .models import AppointmentSlot


class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "doctor", "date", "start_time", "end_time", "status"]

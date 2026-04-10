from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import datetime
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from appointments.models import Appointment, AuditTrail
from availabilitySlots.models import AppointmentSlot
from appointments.serializers import AppointmentSerializer



class CheckInAppointmentView(APIView):
    """
    Checks in a patient for their appointment.
    Transitions status from CONFIRMED to CHECKED_IN and sets check_in_time.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if appointment.status != 'CONFIRMED':
            return Response(
                {"error": f"Cannot check in. Current status is {appointment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            appointment.status = 'CHECKED_IN'
            appointment.check_in_time = timezone.now()
            appointment.save()
            
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

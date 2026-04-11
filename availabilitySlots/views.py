from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from .models import AppointmentSlot
from .serializers import AppointmentSlotSerializer
from .services import generate_slots_for_range
from django.contrib.auth import get_user_model

User = get_user_model()

class DoctorAvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        try:
            doctor = User.objects.get(id=doctor_id, role='DOCTOR')
        except User.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=404)

        today = date.today()
        in_30_days = today + timedelta(days=30)
        generate_slots_for_range(doctor, today, in_30_days)

        from appointments.models import Appointment
        
        # Get all active appointment (date, time) tuples for this doctor
        active_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=today,
            status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']
        ).values_list('appointment_date', 'start_time')
        
        # Initial available slots from DB
        slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            date__gte=today,
            status='AVAILABLE'
        ).order_by('date', 'start_time')

        # Filter out slots that have an matching active appointment tuple
        # This is a fallback in case status synchronization failed for historical data
        active_set = set(active_appointments)
        filtered_slots = [s for s in slots if (s.date, s.start_time) not in active_set]

        serializer = AppointmentSlotSerializer(filtered_slots, many=True)
        return Response(serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from django.core import signing
from .models import AppointmentSlot
from .serializers import AppointmentSlotSerializer
from .services import generate_slots_for_range
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from django.utils import timezone

User = get_user_model()

class DoctorAvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        try:
            doctor = User.objects.get(id=doctor_id, role='DOCTOR')
        except User.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=404)

        
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        in_30_days = today + timedelta(days=30)
        generate_slots_for_range(doctor, today, in_30_days)

        

        active_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=today,
            status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']
        ).values_list('appointment_date', 'start_time')

        slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            date__gte=today,
            status='AVAILABLE'
        ).order_by('date', 'start_time')

        active_set = set(active_appointments)
        
        # Filter: Exclude past times if the date is today
        filtered_slots = []
        for s in slots:
            if (s.date, s.start_time) in active_set:
                continue
            
            if s.date == today and s.start_time <= current_time:
                continue
                
            filtered_slots.append(s)

        serializer = AppointmentSlotSerializer(filtered_slots, many=True)
        slots_with_tokens = []
        for slot_obj, slot_data in zip(filtered_slots, serializer.data):
            token = signing.dumps({'slot_id': slot_obj.id, 'user_id': request.user.id}, salt='booking')
            slot_payload = dict(slot_data)
            slot_payload['booking_token'] = token
            slots_with_tokens.append(slot_payload)

        return Response(slots_with_tokens)
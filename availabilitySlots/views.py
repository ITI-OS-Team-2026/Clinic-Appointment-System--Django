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

        slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            date__gte=today,
            status='AVAILABLE'
        ).order_by('date', 'start_time')

        serializer = AppointmentSlotSerializer(slots, many=True)
        return Response(serializer.data)
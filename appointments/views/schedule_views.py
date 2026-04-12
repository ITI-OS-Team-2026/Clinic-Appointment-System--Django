from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer

class TodayAppointmentsView(APIView):
    """
    Returns a list of today's appointments ordered by start time.
    Only allows access to users with the 'RECEPTIONIST' role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'RECEPTIONIST':
            raise PermissionDenied(detail="Only receptionists can view today's appointments")

        today = timezone.localtime(timezone.now()).date()
        appointments = Appointment.objects.filter(appointment_date=today).order_by('start_time')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

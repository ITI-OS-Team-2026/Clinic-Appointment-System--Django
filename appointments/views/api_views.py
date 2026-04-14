from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import DoctorProfile
from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer

class DoctorListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctors = DoctorProfile.objects.select_related('user').all()
        data = []
        for doc in doctors:
            data.append({
                'id': doc.user.id,
                'full_name': f"Dr. {doc.user.get_full_name() or doc.user.username}",
                'specialization': doc.specialization,
                'experience_years': doc.experience_years,
            })
        return Response(data)

class AppointmentSearchView(APIView):
    """
    Advanced search for appointments.
    Supported filters: doctor_id, start_date, end_date, status, q (patient name).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'RECEPTIONIST':
            return Response({"error": "Unauthorized"}, status=403)

        queryset = Appointment.objects.all().select_related('patient', 'doctor')

        # Filters
        doctor_id = request.query_params.get('doctor_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        query = request.query_params.get('q')

        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if query:
            queryset = queryset.filter(patient__username__icontains=query) | queryset.filter(patient__first_name__icontains=query)

        data = [
            {
                'id': appt.id,
                'patient_name': appt.patient.get_full_name() or appt.patient.username,
                'doctor_name': appt.doctor.get_full_name() or appt.doctor.username,
                'doctor': appt.doctor.id,
                'appointment_date': appt.appointment_date,
                'start_time': appt.start_time.strftime('%H:%M:%S'),
                'end_time': appt.end_time.strftime('%H:%M:%S'),
                'status': appt.status,
            }
            for appt in queryset
        ]
        return Response(data)

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

class ConfirmAppointmentView(APIView):
    """
    Confirms an appointment.
    Transitions status from REQUESTED to CONFIRMED.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if appointment.status != 'REQUESTED':
            return Response(
                {"error": f"Cannot confirm appointment. Current status is {appointment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        appointment.status = 'CONFIRMED'
        appointment.save()
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

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

class RescheduleAppointmentView(APIView):
    """
    Reschedules an appointment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        new_date = request.data.get('new_date')
        new_start = request.data.get('new_start_time')
        new_end = request.data.get('new_end_time')
        reason = request.data.get('reason')
        
        if not all([new_date, new_start, new_end, reason]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
            
        new_slot = AppointmentSlot.objects.filter(
            doctor=appointment.doctor, date=new_date, start_time=new_start, status='AVAILABLE'
        ).first()
        
        if not new_slot:
            return Response({"error": "Selected slot is not available."}, status=status.HTTP_400_BAD_REQUEST)

        old_dt = datetime.datetime.combine(appointment.appointment_date, appointment.start_time)
        new_dt = datetime.datetime.combine(new_slot.date, new_slot.start_time)
        if timezone.is_naive(old_dt): old_dt = timezone.make_aware(old_dt)
        if timezone.is_naive(new_dt): new_dt = timezone.make_aware(new_dt)

        with transaction.atomic():
            # Double check for doctor conflicts even if slot says available (Data Integrity fallback)
            if Appointment.objects.filter(
                doctor=appointment.doctor, 
                appointment_date=new_slot.date, 
                start_time=new_slot.start_time,
                status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']
            ).exclude(id=appointment.id).exists():
                return Response({"error": "This slot was recently taken by another appointment. Please refresh and try again."}, status=status.HTTP_400_BAD_REQUEST)

            old_slot = AppointmentSlot.objects.filter(
                doctor=appointment.doctor, date=appointment.appointment_date, start_time=appointment.start_time
            ).first()
            if old_slot:
                old_slot.status = 'AVAILABLE'
                old_slot.save()
                
            new_slot.status = 'BOOKED'
            new_slot.save()
            
            AuditTrail.objects.create(
                appointment=appointment, changed_by=request.user, 
                old_datetime=old_dt, new_datetime=new_dt, reason=reason
            )
            
            appointment.appointment_date = new_slot.date
            appointment.start_time = new_slot.start_time
            appointment.end_time = new_end
            
            try:
                appointment.save()
            except Exception as e:
                return Response({"error": "An unexpected conflict occurred. Please try a different slot."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(AppointmentSerializer(appointment).data)


class BookAppointmentAPIView(APIView):
    """
    Called by Patients to book an available AppointmentSlot.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        doctor_id = request.data.get('doctor_id')
        date_str = request.data.get('date')
        start_time_str = request.data.get('start_time')
        
        if not all([doctor_id, date_str, start_time_str]):
            return Response({"error": "Missing doctor_id, date, or start_time."}, status=status.HTTP_400_BAD_REQUEST)
            
        slot = AppointmentSlot.objects.filter(
            doctor_id=doctor_id,
            date=date_str,
            start_time=start_time_str,
            status='AVAILABLE'
        ).first()
        
        if not slot:
            return Response({"error": "This slot is not available."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if the patient already has an appointment at this exact time
        if Appointment.objects.filter(patient=request.user, appointment_date=slot.date, start_time=slot.start_time).exists():
            return Response({"error": "You already have an appointment scheduled for this time."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Robust check against data de-sync: verify doctor doesn't have an appointment already
            if Appointment.objects.filter(
                doctor=slot.doctor, 
                appointment_date=slot.date, 
                start_time=slot.start_time,
                status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']
            ).exists():
                return Response({"error": "This slot is already officially booked. Please refresh the page."}, status=status.HTTP_400_BAD_REQUEST)

            slot.status = 'BOOKED'
            slot.save()
            
            try:
                appointment = Appointment.objects.create(
                    patient=request.user,
                    doctor=slot.doctor,
                    appointment_date=slot.date,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    status='REQUESTED'
                )
            except Exception as e:
                return Response({"error": "Failed to create appointment due to a data conflict. Please try another slot."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            "message": "Appointment requested successfully!", 
            "appointment_id": appointment.id
        })

class CompleteAppointmentView(APIView):
    """
    Completes an appointment.
    Transitions status from CHECKED_IN to COMPLETED.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if appointment.status != 'CHECKED_IN':
            return Response(
                {"error": f"Cannot complete. Current status is {appointment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        appointment.status = 'COMPLETED'
        appointment.save()
        
        return Response(AppointmentSerializer(appointment).data)

class NoShowAppointmentView(APIView):
    """
    Marks an appointment as NO_SHOW.
    Transitions status from REQUESTED/CONFIRMED to NO_SHOW.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if appointment.status not in ['REQUESTED', 'CONFIRMED']:
            return Response(
                {"error": f"Cannot mark as No Show. Current status is {appointment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            appointment.status = 'NO_SHOW'
            appointment.save()
            
            # Also free up the slot so others can book it again if desired!
            slot = AppointmentSlot.objects.filter(
                doctor=appointment.doctor,
                date=appointment.appointment_date,
                start_time=appointment.start_time
            ).first()
            if slot:
                slot.status = 'AVAILABLE'
                slot.save()
        
        return Response(AppointmentSerializer(appointment).data)

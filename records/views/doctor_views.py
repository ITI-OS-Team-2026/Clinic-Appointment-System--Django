from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from users.decorators import is_doctor
from appointments.models import Appointment

@user_passes_test(is_doctor)
def doctor_queue(request):
    """View to show today's appointments for the logged-in doctor."""
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date=today
    ).order_by('start_time')

    # Calculate statistics
    stats = {
        'total': appointments.count(),
        'waiting': appointments.filter(status='CHECKED_IN').count(),
        'completed': appointments.filter(status='COMPLETED').count(),
        'confirmed': appointments.filter(status='CONFIRMED').count(),
    }

    return render(request, 'doctor/queue.html', {
        'appointments': appointments,
        'stats': stats,
        'today': today
    })

@user_passes_test(is_doctor)
def booking_requests(request):
    """View to manage pending appointment requests."""
    if request.method == 'POST':
        appt_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        appointment = get_object_or_404(Appointment, id=appt_id, doctor=request.user)

        if action == 'approve':
            appointment.status = 'CONFIRMED'
        elif action == 'decline':
            appointment.status = 'CANCELLED'
        
        appointment.save()
        return redirect('booking_requests')

    # Get all requested appointments for this doctor
    requests = Appointment.objects.filter(
        doctor=request.user,
        status='REQUESTED'
    ).order_by('appointment_date', 'start_time')

    return render(request, 'doctor/booking_requests.html', {
        'booking_requests': requests
    })

@user_passes_test(is_doctor)
def appointment_diagnosis(request, appointment_id):
    """View to enter diagnosis and prescriptions after a session."""
    from records.models import ConsultationRecord, PrescriptionItem
    from django.db import transaction
    import json

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        notes = request.POST.get('notes')
        requested_tests = request.POST.get('requested_tests')
        prescriptions_json = request.POST.get('prescriptions_data')

        with transaction.atomic():
            # Create the consultation record
            consultation = ConsultationRecord.objects.create(
                appointment=appointment,
                diagnosis=diagnosis,
                notes=notes,
                requested_tests=requested_tests
            )

            # Create prescriptions if provided
            if prescriptions_json:
                prescriptions = json.loads(prescriptions_json)
                for item in prescriptions:
                    PrescriptionItem.objects.create(
                        consultation=consultation,
                        drug_name=item.get('drug_name'),
                        dose=item.get('dose'),
                        duration=item.get('duration')
                    )

            # Ensure appointment status is COMPLETED
            appointment.status = 'COMPLETED'
            appointment.save()

        return redirect('doctor_queue')

    return render(request, 'doctor/diagnosis_form.html', {
        'appointment': appointment
    })

@user_passes_test(is_doctor)
def doctor_schedule(request):
    """View to show the doctor's weekly work schedule (Read-only)."""
    from appointments.models import DoctorSchedule
    schedule = DoctorSchedule.objects.filter(doctor=request.user).order_by('day_of_week', 'start_time')
    
    # Map day integers to names for cleaner display if needed, 
    # but we'll handle it in the template for better formatting.
    return render(request, 'doctor/schedule.html', {
        'schedule': schedule
    })

@user_passes_test(is_doctor)
def doctor_profile(request):
    """View to show the doctor's professional profile (Read-only)."""
    # Profile is created via signals, so it should exist.
    profile = getattr(request.user, 'doctor_profile', None)
    return render(request, 'doctor/profile.html', {
        'profile': profile,
        'doctor_user': request.user
    })


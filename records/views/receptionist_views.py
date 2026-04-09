from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from users.decorators import is_receptionist
from appointments.models import Appointment


@user_passes_test(is_receptionist, login_url='/users/login/')
def receptionist_queue(request):
    today = timezone.now().date()
    now = timezone.now()

    appointments = Appointment.objects.filter(
        appointment_date=today,
        status__in=['CONFIRMED', 'CHECKED_IN']
    ).select_related('patient', 'doctor').order_by('start_time')

    return render(request, 'receptionist/queue.html', {
        'appointments': appointments,
        'today': today,
        'now': now,
    })


@user_passes_test(is_receptionist, login_url='/users/login/')
def check_in_patient(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        appt.status = 'CHECKED_IN'
        appt.check_in_time = timezone.now()
        appt.save()

    return redirect('receptionist_queue')
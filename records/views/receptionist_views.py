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
def appointment_management(request):
    """
    Renders the master Appointment Search & Management layout.
    """
    return render(request, 'receptionist/management.html')

@user_passes_test(is_receptionist, login_url='/users/login/')
def receptionist_profile(request):
    """
    View to display and allow basic profile updates (First/Last name only).
    """
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        return redirect('receptionist_profile')
        
    return render(request, 'receptionist/profile.html', {
        'user': user
    })

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from users.decorators import is_patient
from appointments.models import Appointment
from users.models import PatientProfile


@user_passes_test(is_patient, login_url='/users/login/')
def patient_dashboard(request):
    profile = PatientProfile.objects.get(user=request.user)
    appts = Appointment.objects.filter(patient=request.user)

    upcoming = appts.filter(status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']).order_by('appointment_date', 'start_time')
    past = appts.filter(status__in=['COMPLETED', 'CANCELLED', 'NO_SHOW']).order_by('-appointment_date', '-start_time')

    context = {
        'profile': profile,
        'upcoming': upcoming,
        'past': past,
        'total': appts.count(),
        'completed_count': past.filter(status='COMPLETED').count(),
        'cancelled_count': past.filter(status='CANCELLED').count()
    }
    return render(request, 'patient/dashboard.html', context)


@user_passes_test(is_patient, login_url='/users/login/')
def patient_book_appointment(request):
    return render(request, 'patient/book_appointment.html')
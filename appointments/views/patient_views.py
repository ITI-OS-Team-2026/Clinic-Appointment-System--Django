from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from users.decorators import is_patient

@user_passes_test(is_patient, login_url='/users/login/')
def patient_dashboard(request):
    return HttpResponse("<h1>Patient Dashboard</h1><a href='/users/logout/'>Logout</a>")

@user_passes_test(is_patient, login_url='/users/login/')
def patient_book_appointment(request):
    return render(request, 'patient/book_appointment.html')
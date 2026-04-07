from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from users.decorators import is_patient

@user_passes_test(is_patient)
def patient_dashboard(request):
    return HttpResponse("<h1>Patient Dashboard</h1><a href='/users/logout/'>Logout</a>")
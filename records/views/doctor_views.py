from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from users.decorators import is_doctor

@user_passes_test(is_doctor)
def doctor_queue(request):
    return HttpResponse("<h1>Doctor Queue</h1><a href='/users/logout/'>Logout</a>")
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from users.decorators import is_receptionist

@user_passes_test(is_receptionist)
def receptionist_queue(request):
    return HttpResponse("<h1>Receptionist Queue</h1><a href='/users/logout/'>Logout</a>")
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from ..decorators import is_admin_role

@user_passes_test(is_admin_role)
def admin_dashboard(request):
    return HttpResponse("<h1>Admin Dashboard</h1><a href='/users/logout/'>Logout</a>")
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def is_patient(user):
    if user.is_authenticated and user.role == 'PATIENT':
        return True
    raise PermissionDenied

def is_doctor(user):
    if user.is_authenticated and user.role == 'DOCTOR':
        return True
    raise PermissionDenied

def is_receptionist(user):
    if user.is_authenticated and user.role == 'RECEPTIONIST':
        return True
    raise PermissionDenied

def is_admin_role(user):
    if user.is_authenticated and user.role == 'ADMIN':
        return True
    raise PermissionDenied

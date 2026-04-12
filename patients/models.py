from django.db import models
from users.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5)
    gender = models.CharField(max_length=20)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    emergency_contact_name=models.CharField(max_length=100,blank=True)
    emergency_contact_number=models.CharField(max_length=20,blank=True)
    medical_notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)    
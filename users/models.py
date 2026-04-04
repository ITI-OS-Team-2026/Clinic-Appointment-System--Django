from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('RECEPTIONIST', 'Receptionist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    bio = models.TextField()
    experience_years = models.IntegerField()
    contact_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5)
    gender = models.CharField(max_length=20)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
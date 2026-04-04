from django.db import models
from appointments.models import Appointment

class ConsultationRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation_record')
    diagnosis = models.TextField()
    notes = models.TextField()
    requested_tests = models.TextField(blank=True)

class PrescriptionItem(models.Model):
    consultation = models.ForeignKey(ConsultationRecord, on_delete=models.CASCADE, related_name='prescriptions')
    drug_name = models.CharField(max_length=255)
    dose = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
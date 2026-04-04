from django.db import models
from django.conf import settings

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_duration_mins = models.IntegerField(default=30)
    buffer_duration_mins = models.IntegerField(default=5)

class ScheduleException(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exceptions')
    exception_date = models.DateField()
    is_day_off = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Requested'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    )
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    check_in_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'appointment_date', 'start_time'], name='unique_doctor_slot'),
            models.UniqueConstraint(fields=['patient', 'appointment_date', 'start_time'], name='unique_patient_slot')
        ]

class AuditTrail(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='audit_history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_datetime = models.DateTimeField()
    new_datetime = models.DateTimeField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
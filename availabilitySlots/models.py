from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()




class AppointmentSlot(models.Model):
    """A concrete bookable slot generated from the schedule"""
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BOOKED',    'Booked'),
        ('BLOCKED',   'Blocked'),]
    doctor     = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='slots')
    date       = models.DateField()
    start_time = models.TimeField()
    end_time   = models.TimeField()
    status     = models.CharField(max_length=10,
                                  choices=STATUS_CHOICES, default='AVAILABLE')

    class Meta:
        unique_together = ['doctor', 'date', 'start_time']

    def __str__(self):
        return f"Dr.{self.doctor} | {self.date} {self.start_time}-{self.end_time} [{self.status}]"
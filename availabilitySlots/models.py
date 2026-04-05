from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DoctorWeeklySchedule(models.Model):
    """Defines a doctor's recurring weekly hours"""
    DAYS = [(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),
            (3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')]

    doctor      = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='weekly_schedules')
    day_of_week = models.IntegerField(choices=DAYS) 
    start_time  = models.TimeField()  
    end_time    = models.TimeField()  
    slot_duration_minutes = models.IntegerField(default=30)  
    buffer_minutes        = models.IntegerField(default=5)

    class Meta:
        unique_together = ['doctor', 'day_of_week']

    def __str__(self):
        return f"Dr.{self.doctor} - {self.get_day_of_week_display()}"


class DoctorScheduleException(models.Model):
    """Day off OR a special one-off working day"""
    EXCEPTION_TYPES = [
        ('DAY_OFF', 'Day Off / Vacation'),
        ('EXTRA',   'Extra Working Day'),
    ]
    doctor         = models.ForeignKey(User, on_delete=models.CASCADE,
                                       related_name='schedule_exceptions')
    date           = models.DateField()
    exception_type = models.CharField(max_length=10, choices=EXCEPTION_TYPES)
    # Only filled when type=EXTRA (override hours for that day)
    start_time     = models.TimeField(null=True, blank=True)
    end_time       = models.TimeField(null=True, blank=True)
    reason         = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ['doctor', 'date']


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
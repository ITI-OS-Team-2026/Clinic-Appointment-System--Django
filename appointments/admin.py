from django.contrib import admin
from .models import Appointment, AuditTrail, DoctorSchedule, ScheduleException

admin.site.register(Appointment)
admin.site.register(AuditTrail)
admin.site.register(DoctorSchedule)
admin.site.register(ScheduleException)

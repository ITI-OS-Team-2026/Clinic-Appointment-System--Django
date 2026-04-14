from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Appointment
from availabilitySlots.models import AppointmentSlot

@receiver(post_delete, sender=Appointment)
def sync_slot_on_delete(sender, instance, **kwargs):
    """
    When an Appointment is deleted, find the matching AppointmentSlot
    and set its status back to 'AVAILABLE'.
    """
    AppointmentSlot.objects.filter(
        doctor=instance.doctor,
        date=instance.appointment_date,
        start_time=instance.start_time
    ).update(status='AVAILABLE')

@receiver(post_save, sender=Appointment)
def sync_slot_on_status_change(sender, instance, created, **kwargs):
    """
    When an Appointment status changes to 'CANCELLED' or 'NO_SHOW',
    set the matching AppointmentSlot back to 'AVAILABLE'.
    """
    if instance.status in ['CANCELLED', 'NO_SHOW' ,"COMPLETED"]:
        AppointmentSlot.objects.filter(
            doctor=instance.doctor,
            date=instance.appointment_date,
            start_time=instance.start_time
        ).update(status='AVAILABLE')

    elif instance.status in ['REQUESTED', 'CONFIRMED', 'CHECKED_IN']:
        AppointmentSlot.objects.filter(
            doctor=instance.doctor,
            date=instance.appointment_date,
            start_time=instance.start_time
        ).update(status='BOOKED')

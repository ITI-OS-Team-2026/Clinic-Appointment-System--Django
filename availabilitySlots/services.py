from datetime import datetime, timedelta, date
from .models import AppointmentSlot
from appointments.models import DoctorSchedule, ScheduleException

def generate_slots_for_date(doctor, target_date: date):
    AppointmentSlot.objects.filter(
        doctor=doctor,
        date=target_date,
        status='AVAILABLE'
    ).delete()

    try:
        exception = ScheduleException.objects.get(
            doctor=doctor, exception_date=target_date
        )
        if exception.is_day_off:
            return []

        start_time = exception.start_time
        end_time   = exception.end_time
        slot_duration = 30
        buffer        = 5

    except ScheduleException.DoesNotExist:
        day_of_week = target_date.weekday()
        schedule = DoctorSchedule.objects.filter(
            doctor=doctor, day_of_week=day_of_week
        ).first()

        if not schedule:
            return []

        start_time    = schedule.start_time
        end_time      = schedule.end_time
        slot_duration = schedule.session_duration_mins
        buffer        = schedule.buffer_duration_mins

    slots_created = []
    current = datetime.combine(target_date, start_time)
    shift_end = datetime.combine(target_date, end_time)
    slot_delta   = timedelta(minutes=slot_duration)
    buffer_delta = timedelta(minutes=buffer)

    while current + slot_delta <= shift_end:
        slot_end = current + slot_delta
        from appointments.models import Appointment
        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=target_date,
            start_time=current.time(),
            status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']
        ).exists()

        initial_status = 'BOOKED' if exists else 'AVAILABLE'

        slot, created = AppointmentSlot.objects.get_or_create(
            doctor     = doctor,
            date       = target_date,
            start_time = current.time(),
            defaults={
                'end_time': slot_end.time(),
                'status':   initial_status,
            }
        )
        if created:
            slots_created.append(slot)
        current = slot_end + buffer_delta
    return slots_created

def generate_slots_for_range(doctor, from_date: date, to_date: date):
    all_slots = []
    current_date = from_date
    one_day = timedelta(days=1)

    while current_date <= to_date:
        slots = generate_slots_for_date(doctor, current_date)
        all_slots.extend(slots)
        current_date += one_day

    return all_slots
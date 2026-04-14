from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from users.decorators import is_doctor
from appointments.models import Appointment

@user_passes_test(is_doctor)
def doctor_queue(request):
    """View to show today's appointments for the logged-in doctor."""
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date=today
    ).order_by('start_time')

    stats = {
        'total': appointments.count(),
        'waiting': appointments.filter(status='CHECKED_IN').count(),
        'completed': appointments.filter(status='COMPLETED').count(),
        'confirmed': appointments.filter(status='CONFIRMED').count(),
    }

    return render(request, 'doctor/queue.html', {
        'appointments': appointments,
        'stats': stats,
        'today': today
    })

@user_passes_test(is_doctor)
def booking_requests(request):
    """View to manage pending appointment requests."""
    if request.method == 'POST':
        appt_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        appointment = get_object_or_404(Appointment, id=appt_id, doctor=request.user)

        if action == 'approve':
            appointment.status = 'CONFIRMED'
        elif action == 'decline':
            appointment.status = 'CANCELLED'

        appointment.save()
        return redirect('booking_requests')

    requests = Appointment.objects.filter(
        doctor=request.user,
        status='REQUESTED'
    ).order_by('appointment_date', 'start_time')

    return render(request, 'doctor/booking_requests.html', {
        'booking_requests': requests
    })

@user_passes_test(is_doctor)
def appointment_diagnosis(request, appointment_id):
    """View to enter diagnosis and prescriptions after a session."""
    from records.models import ConsultationRecord, PrescriptionItem
    from django.db import transaction
    import json

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        notes = request.POST.get('notes')
        requested_tests = request.POST.get('requested_tests')
        prescriptions_json = request.POST.get('prescriptions_data')

        with transaction.atomic():
            consultation = ConsultationRecord.objects.create(
                appointment=appointment,
                diagnosis=diagnosis,
                notes=notes,
                requested_tests=requested_tests
            )

            if prescriptions_json:
                prescriptions = json.loads(prescriptions_json)
                for item in prescriptions:
                    PrescriptionItem.objects.create(
                        consultation=consultation,
                        drug_name=item.get('drug_name'),
                        dose=item.get('dose'),
                        duration=item.get('duration')
                    )

            appointment.status = 'COMPLETED'
            appointment.save()

        return redirect('doctor_queue')

    return render(request, 'doctor/diagnosis_form.html', {
        'appointment': appointment
    })

@user_passes_test(is_doctor)
def doctor_schedule(request):
    """View to show the doctor's weekly work schedule (Read-only)."""
    from appointments.models import DoctorSchedule
    schedule = DoctorSchedule.objects.filter(doctor=request.user).order_by('day_of_week', 'start_time')

    return render(request, 'doctor/schedule.html', {
        'schedule': schedule
    })

@user_passes_test(is_doctor)
def doctor_profile(request):
    """View to show the doctor's professional profile (Read-only)."""
    profile = getattr(request.user, 'doctor_profile', None)
    return render(request, 'doctor/profile.html', {
        'profile': profile,
        'doctor_user': request.user
    })

@user_passes_test(is_doctor)
def doctor_monthly_planner(request):
    """View to plan and finalize the doctor's schedule for an entire month."""
    import calendar
    from datetime import date, datetime
    from appointments.models import ScheduleException
    from availabilitySlots.services import generate_slots_for_date

    now = timezone.now()
    try:
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', (now.month % 12) + 1))
        if now.month == 12 and not request.GET.get('year'):
            year = now.year + 1
    except (ValueError, TypeError):
        year, month = now.year, (now.month % 12) + 1

    work_days_ids = []
    day_times = {}
    conflicts = []

    days_in_month = calendar.monthrange(year, month)[1]
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)

    existing_exceptions = ScheduleException.objects.filter(
        doctor=request.user,
        exception_date__range=[first_day, last_day]
    ).order_by('exception_date')

    is_finalized = existing_exceptions.exists()
    work_count = existing_exceptions.filter(is_day_off=False).count()
    off_count = existing_exceptions.filter(is_day_off=True).count()

    work_days_ids = []
    day_times = {}
    if is_finalized:
        active_work_days = existing_exceptions.filter(is_day_off=False)
        for ex in active_work_days:
            wd = ex.exception_date.weekday()
            if wd not in work_days_ids:
                work_days_ids.append(wd)
                day_times[wd] = {
                    'start': ex.start_time.strftime('%H:%M') if ex.start_time else '09:00',
                    'end': ex.end_time.strftime('%H:%M') if ex.end_time else '17:00'
                }

    if request.method == 'POST':
        if 'reset_month' in request.POST:
            is_finalized = False
            from django.contrib import messages
            messages.info(request, f"Review and update your schedule for {calendar.month_name[month]}. Click Update when finished.")
        else:
            working_days = [int(d) for d in request.POST.getlist('working_days')]
            work_days_ids = working_days

            from appointments.models import Appointment, AuditTrail
            conflicts = []
            for day in range(1, days_in_month + 1):
                target_date = date(year, month, day)
                if target_date.weekday() not in working_days:
                    booked = Appointment.objects.filter(
                        doctor=request.user,
                        appointment_date=target_date,
                        status__in=['SCHEDULED', 'CONFIRMED', 'REQUESTED']
                    )
                    if booked.exists():
                        conflicts.extend(list(booked))

            if conflicts and not request.POST.get('confirm_conflicts'):
                for wd in working_days:
                    start = request.POST.get(f'start_time_{wd}', '09:00')
                    end = request.POST.get(f'end_time_{wd}', '17:00')
                    day_times[wd] = {'start': start, 'end': end}

                return render(request, 'doctor/monthly_planner.html', {
                    'year': year, 'month': month, 'month_name': calendar.month_name[month],
                    'is_finalized': is_finalized, 'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
                    'years': [now.year, now.year + 1], 'exceptions': existing_exceptions,
                    'work_count': work_count, 'off_count': off_count,
                    'work_days_ids': working_days,
                    'day_times': day_times,
                    'conflicts': conflicts
                })

            if conflicts and request.POST.get('confirm_conflicts'):
                from django.db import transaction
                with transaction.atomic():
                    for apt in conflicts:
                        old_dt = timezone.datetime.combine(apt.appointment_date, apt.start_time)
                        if timezone.is_naive(old_dt): old_dt = timezone.make_aware(old_dt)

                        AuditTrail.objects.create(
                            appointment=apt, changed_by=request.user,
                            old_datetime=old_dt, new_datetime=old_dt,
                            reason="Monthly Schedule Update: Appointment cancelled due to doctor schedule change."
                        )

                        apt.status = 'CANCELLED'
                        apt.save()

                        from availabilitySlots.models import AppointmentSlot
                        slot = AppointmentSlot.objects.filter(
                            doctor=request.user, date=apt.appointment_date, start_time=apt.start_time
                        ).first()
                        if slot:
                            slot.status = 'AVAILABLE'
                            slot.save()

            from availabilitySlots.models import AppointmentSlot
            for day in range(1, days_in_month + 1):
                target_date = date(year, month, day)
                weekday = target_date.weekday()

                if weekday in working_days:
                    start_str = request.POST.get(f'start_time_{weekday}', '09:00')
                    end_str = request.POST.get(f'end_time_{weekday}', '17:00')
                    start_time = datetime.strptime(start_str, '%H:%M').time()
                    end_time = datetime.strptime(end_str, '%H:%M').time()

                    ScheduleException.objects.update_or_create(
                        doctor=request.user, exception_date=target_date,
                        defaults={'is_day_off': False, 'start_time': start_time, 'end_time': end_time}
                    )
                else:
                    ScheduleException.objects.update_or_create(
                        doctor=request.user, exception_date=target_date,
                        defaults={'is_day_off': True, 'start_time': None, 'end_time': None}
                    )
                generate_slots_for_date(request.user, target_date)

            from django.contrib import messages
            messages.success(request, f"Schedule for {calendar.month_name[month]} {year} has been updated.")
            return redirect(f"{request.path}?month={month}&year={year}")

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [now.year, now.year + 1]

    return render(request, 'doctor/monthly_planner.html', {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'is_finalized': is_finalized,
        'months': months,
        'years': years,
        'exceptions': existing_exceptions,
        'work_count': work_count,
        'off_count': off_count,
        'work_days_ids': work_days_ids,
        'day_times': day_times
    })

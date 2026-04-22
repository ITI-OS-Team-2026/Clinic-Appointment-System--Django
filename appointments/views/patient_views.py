import datetime
import urllib.parse

from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from appointments.models import Appointment, AuditTrail
from availabilitySlots.models import AppointmentSlot
from users.decorators import is_patient
from users.models import DoctorProfile, PatientProfile


def _paginator_range(page_obj, num_pages):
    page = page_obj.number
    total = num_pages
    if total <= 7:
        return list(range(1, total + 1))
    if page <= 4:
        return list(range(1, 6)) + [None, total]
    if page >= total - 3:
        return [1, None] + list(range(total - 4, total + 1))
    return [1, None, page - 1, page, page + 1, None, total]


@user_passes_test(is_patient, login_url="/users/login/")
def patient_dashboard(request):
    profile = PatientProfile.objects.get(user=request.user)
    appts = Appointment.objects.filter(patient=request.user).select_related("doctor")

    upcoming_qs = appts.filter(status__in=["REQUESTED", "CONFIRMED", "CHECKED_IN"])

    upcoming_doctor = request.GET.get("upcoming_doctor", "")
    upcoming_status = request.GET.get("upcoming_status", "")
    upcoming_date_from = request.GET.get("upcoming_date_from", "")
    upcoming_date_to = request.GET.get("upcoming_date_to", "")

    if upcoming_doctor:
        upcoming_qs = upcoming_qs.filter(doctor_id=upcoming_doctor)
    if upcoming_status:
        upcoming_qs = upcoming_qs.filter(status=upcoming_status)
    if upcoming_date_from:
        upcoming_qs = upcoming_qs.filter(appointment_date__gte=upcoming_date_from)
    if upcoming_date_to:
        upcoming_qs = upcoming_qs.filter(appointment_date__lte=upcoming_date_to)

    upcoming_qs = upcoming_qs.order_by("appointment_date", "start_time")

    upcoming_paginator = Paginator(upcoming_qs, 5)
    try:
        upcoming_page = upcoming_paginator.page(request.GET.get("upcoming_page", 1))
    except (PageNotAnInteger, EmptyPage):
        upcoming_page = upcoming_paginator.page(1)

    past_qs = appts.filter(status__in=["COMPLETED", "CANCELLED", "NO_SHOW"])

    past_doctor = request.GET.get("past_doctor", "")
    past_status = request.GET.get("past_status", "")
    past_date_from = request.GET.get("past_date_from", "")
    past_date_to = request.GET.get("past_date_to", "")

    if past_doctor:
        past_qs = past_qs.filter(doctor_id=past_doctor)
    if past_status:
        past_qs = past_qs.filter(status=past_status)
    if past_date_from:
        past_qs = past_qs.filter(appointment_date__gte=past_date_from)
    if past_date_to:
        past_qs = past_qs.filter(appointment_date__lte=past_date_to)

    past_qs = past_qs.order_by("-appointment_date", "-start_time")

    past_paginator = Paginator(past_qs, 10)
    try:
        past_page = past_paginator.page(request.GET.get("past_page", 1))
    except (PageNotAnInteger, EmptyPage):
        past_page = past_paginator.page(1)

    doctor_ids = appts.values_list("doctor_id", flat=True).distinct()
    doctors = DoctorProfile.objects.filter(user_id__in=doctor_ids).select_related(
        "user"
    )

    doctor_name_map = {str(d.user_id): d.user.get_full_name() for d in doctors}
    upcoming_doctor_name = (
        "Dr. " + doctor_name_map.get(upcoming_doctor, upcoming_doctor)
        if upcoming_doctor
        else ""
    )
    past_doctor_name = (
        "Dr. " + doctor_name_map.get(past_doctor, past_doctor) if past_doctor else ""
    )

    STATUS_LABELS = {
        "REQUESTED": "Requested",
        "CONFIRMED": "Confirmed",
        "CHECKED_IN": "Checked In",
        "COMPLETED": "Completed",
        "CANCELLED": "Cancelled",
        "NO_SHOW": "No Show",
    }

    past_all_params = {
        k: v for k, v in request.GET.items() if k.startswith("past_") and v
    }
    upcoming_all_params = {
        k: v for k, v in request.GET.items() if k.startswith("upcoming_") and v
    }
    past_all_qs = urllib.parse.urlencode(past_all_params)
    upcoming_all_qs = urllib.parse.urlencode(upcoming_all_params)
    upcoming_pagination_qs = urllib.parse.urlencode(
        {k: v for k, v in request.GET.items() if k != "upcoming_page" and v}
    )
    past_pagination_qs = urllib.parse.urlencode(
        {k: v for k, v in request.GET.items() if k != "past_page" and v}
    )

    context = {
        "profile": profile,
        "upcoming": upcoming_page,
        "past": past_page,
        "doctors": doctors,
        "upcoming_filters": {
            "doctor": upcoming_doctor,
            "status": upcoming_status,
            "date_from": upcoming_date_from,
            "date_to": upcoming_date_to,
            "doctor_name": upcoming_doctor_name,
            "status_label": STATUS_LABELS.get(upcoming_status, ""),
        },
        "past_filters": {
            "doctor": past_doctor,
            "status": past_status,
            "date_from": past_date_from,
            "date_to": past_date_to,
            "doctor_name": past_doctor_name,
            "status_label": STATUS_LABELS.get(past_status, ""),
        },
        "past_all_params": past_all_params,
        "upcoming_all_params": upcoming_all_params,
        "past_all_qs": past_all_qs,
        "upcoming_all_qs": upcoming_all_qs,
        "upcoming_pagination_qs": upcoming_pagination_qs,
        "past_pagination_qs": past_pagination_qs,
        "upcoming_page_range": _paginator_range(
            upcoming_page, upcoming_paginator.num_pages
        ),
        "past_page_range": _paginator_range(past_page, past_paginator.num_pages),
        "total": appts.count(),
        "upcoming_count": appts.filter(
            status__in=["REQUESTED", "CONFIRMED", "CHECKED_IN"]
        ).count(),
        "completed_count": appts.filter(status="COMPLETED").count(),
        "cancelled_count": appts.filter(status="CANCELLED").count(),
    }
    return render(request, "patient/dashboard.html", context)


@user_passes_test(is_patient, login_url="/users/login/")
def cancel_appointment(request, appointment_id):
    if request.method == "POST":
        appt = get_object_or_404(Appointment, id=appointment_id)
        if appt.patient == request.user and appt.status in ["REQUESTED", "CONFIRMED"]:
            appt.status = "CANCELLED"
            appt.save()
    return redirect("patient_dashboard")


@user_passes_test(is_patient, login_url="/users/login/")
def patient_reschedule_appointment(request, appointment_id):
    if request.method == "POST":
        appt = get_object_or_404(Appointment, id=appointment_id)
        if appt.patient == request.user and appt.status in ["REQUESTED", "CONFIRMED"]:
            new_date = request.POST.get("new_date")
            new_start = request.POST.get("new_start_time")
            reason = request.POST.get("reason", "Rescheduled by patient")

            if new_date and new_start:
                new_slot = AppointmentSlot.objects.filter(
                    doctor=appt.doctor,
                    date=new_date,
                    start_time=new_start,
                    status="AVAILABLE",
                ).first()

                if new_slot:
                    old_dt = datetime.datetime.combine(
                        appt.appointment_date, appt.start_time
                    )
                    new_dt = datetime.datetime.combine(
                        new_slot.date, new_slot.start_time
                    )
                    if timezone.is_naive(old_dt):
                        old_dt = timezone.make_aware(old_dt)
                    if timezone.is_naive(new_dt):
                        new_dt = timezone.make_aware(new_dt)

                    old_slot = AppointmentSlot.objects.filter(
                        doctor=appt.doctor,
                        date=appt.appointment_date,
                        start_time=appt.start_time,
                    ).first()
                    if old_slot:
                        old_slot.status = "AVAILABLE"
                        old_slot.save()

                    new_slot.status = "BOOKED"
                    new_slot.save()

                    AuditTrail.objects.create(
                        appointment=appt,
                        changed_by=request.user,
                        old_datetime=old_dt,
                        new_datetime=new_dt,
                        reason=reason,
                    )

                    appt.appointment_date = new_slot.date
                    appt.start_time = new_slot.start_time
                    appt.end_time = new_slot.end_time
                    appt.save()

    return redirect("patient_dashboard")


@user_passes_test(is_patient, login_url="/users/login/")
def patient_book_appointment(request):
    specialty = request.GET.get("specialty", "")
    page = request.GET.get("page", 1)

    doctors = DoctorProfile.objects.select_related("user").all()

    specialties = list(
        DoctorProfile.objects.values_list("specialization", flat=True).distinct()
    )
    specialties = [s for s in specialties if s]

    if specialty:
        doctors = doctors.filter(specialization__iexact=specialty)

    paginator = Paginator(doctors, 8)

    try:
        doctors_page = paginator.page(page)
    except PageNotAnInteger:
        doctors_page = paginator.page(1)
    except EmptyPage:
        doctors_page = paginator.page(paginator.num_pages)

    context = {
        "doctors_page": doctors_page,
        "specialties": specialties,
        "current_specialty": specialty,
        "is_paginated": doctors_page.has_other_pages(),
    }
    return render(request, "patient/book_appointment.html", context)

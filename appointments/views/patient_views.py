from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from users.decorators import is_patient
from appointments.models import Appointment, AuditTrail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from users.models import PatientProfile, DoctorProfile
from availabilitySlots.models import AppointmentSlot
from django.utils import timezone
import datetime
@user_passes_test(is_patient, login_url='/users/login/')
def patient_dashboard(request):
    profile = PatientProfile.objects.get(user=request.user)
    appts = Appointment.objects.filter(patient=request.user)

    upcoming = appts.filter(status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']).order_by('appointment_date', 'start_time')
    past = appts.filter(status__in=['COMPLETED', 'CANCELLED', 'NO_SHOW']).order_by('-appointment_date', '-start_time')

    context = {
        'profile': profile,
        'upcoming': upcoming,
        'past': past,
        'total': appts.count(),
        'completed_count': past.filter(status='COMPLETED').count(),
        'cancelled_count': past.filter(status='CANCELLED').count()
    }
    return render(request, 'patient/dashboard.html', context)

@user_passes_test(is_patient, login_url='/users/login/')
def cancel_appointment(request, appointment_id):
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appointment_id)
        if appt.patient == request.user and appt.status in ['REQUESTED', 'CONFIRMED']:
            appt.status = 'CANCELLED'
            appt.save()
    return redirect('patient_dashboard')

@user_passes_test(is_patient, login_url='/users/login/')
def patient_reschedule_appointment(request, appointment_id):
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appointment_id)
        if appt.patient == request.user and appt.status in ['REQUESTED', 'CONFIRMED']:
            new_date = request.POST.get('new_date')
            new_start = request.POST.get('new_start_time')
            reason = request.POST.get('reason', 'Rescheduled by patient')

            if new_date and new_start:
                new_slot = AppointmentSlot.objects.filter(
                    doctor=appt.doctor, date=new_date, start_time=new_start, status='AVAILABLE'
                ).first()

                if new_slot:
                    old_dt = datetime.datetime.combine(appt.appointment_date, appt.start_time)
                    new_dt = datetime.datetime.combine(new_slot.date, new_slot.start_time)
                    if timezone.is_naive(old_dt): old_dt = timezone.make_aware(old_dt)
                    if timezone.is_naive(new_dt): new_dt = timezone.make_aware(new_dt)

                    old_slot = AppointmentSlot.objects.filter(
                        doctor=appt.doctor, date=appt.appointment_date, start_time=appt.start_time
                    ).first()
                    if old_slot:
                        old_slot.status = 'AVAILABLE'
                        old_slot.save()

                    new_slot.status = 'BOOKED'
                    new_slot.save()

                    AuditTrail.objects.create(
                        appointment=appt, changed_by=request.user,
                        old_datetime=old_dt, new_datetime=new_dt, reason=reason
                    )

                    appt.appointment_date = new_slot.date
                    appt.start_time = new_slot.start_time
                    appt.end_time = new_slot.end_time
                    appt.save()

    return redirect('patient_dashboard')

@user_passes_test(is_patient, login_url='/users/login/')
def patient_book_appointment(request):
    specialty = request.GET.get('specialty', '')
    page = request.GET.get('page', 1)

    doctors = DoctorProfile.objects.select_related('user').all()
    
    specialties = list(DoctorProfile.objects.values_list('specialization', flat=True).distinct())
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
        'doctors_page': doctors_page,
        'specialties': specialties,
        'current_specialty': specialty,
        'is_paginated': doctors_page.has_other_pages(),
    }
    return render(request, 'patient/book_appointment.html', context)
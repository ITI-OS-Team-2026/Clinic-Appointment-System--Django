from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from ..decorators import is_admin_role
from users.models import User, DoctorProfile
import csv
from django.http import HttpResponse

def admin_dashboard(request):
    # Get recent patient registrations from last 24 hours
    last_24h = timezone.now() - timedelta(hours=24)
    recent_patients = User.objects.filter(
        role='PATIENT',
        date_joined__gte=last_24h
    ).order_by('-date_joined')[:5]
    
    context = {
        'recent_patients': recent_patients
    }
    return render(request, 'admin/dashboard.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin_role)
def add_doctor(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        e = request.POST.get('email')
        
        bio = request.POST.get('bio')
        exp = request.POST.get('experience_years')
        phone = request.POST.get('contact_number')
        loc = request.POST.get('location')
        spec = request.POST.get('specialization')
        license_num = request.POST.get('license_number')

        if User.objects.filter(username=u).exists():
            messages.error(request, "That username is already taken.")
            return redirect('add_doctor')

        user = User.objects.create_user(username=u, email=e, password=p, role='DOCTOR')
        
        DoctorProfile.objects.create(
            user=user, 
            bio=bio, 
            experience_years=exp, 
            contact_number=phone,
            location=loc,
            specialization=spec,
            license_number=license_num
        )
        
        messages.success(request, f"Dr. {u} was successfully added to the clinic!")
        return redirect('admin_dashboard')

    return render(request, 'admin/add_doctor.html')

@login_required(login_url='login')
@user_passes_test(is_admin_role)
def add_receptionist(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        e = request.POST.get('email')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, "That username is already taken.")
            return redirect('add_receptionist')

        User.objects.create_user(username=u, email=e, password=p, role='RECEPTIONIST')
        
        messages.success(request, f"Receptionist {u} was successfully added to the staff!")
        return redirect('admin_dashboard')

    return render(request, 'admin/add_receptionist.html')

@login_required(login_url='login')
@user_passes_test(is_admin_role)
def analytics(request):
    from appointments.models import Appointment
    from django.db.models import Count, Q
    
    # total counts
    total_patients = User.objects.filter(role='PATIENT').count()
    total_doctors = User.objects.filter(role='DOCTOR').count()
    total_appointments = Appointment.objects.count()
    total_receptionists = User.objects.filter(role='RECEPTIONIST').count()
    
    # Appointment status breakdown
    appointment_statuses = Appointment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # completed appointments
    completed_appointments = Appointment.objects.filter(status='COMPLETED').count()
    confirmed_appointments = Appointment.objects.filter(status='CONFIRMED').count()
    cancelled_appointments = Appointment.objects.filter(status='CANCELLED').count()
    
    # top doctors by appointments
    top_doctors = User.objects.filter(role='DOCTOR').annotate(
        appointment_count=Count('appointments_as_doctor')
    ).order_by('-appointment_count')[:5]
    
    # appointment in last 7 days
    last_7_days = timezone.now() - timedelta(days=7)
    appointments_last_week = Appointment.objects.filter(
        appointment_date__gte=last_7_days.date()
    ).count()
    
    # new registrations this month
    this_month = timezone.now()
    new_registrations_this_month = User.objects.filter(
        role='PATIENT',
        date_joined__month=this_month.month,
        date_joined__year=this_month.year
    ).count()
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'total_receptionists': total_receptionists,
        'appointment_statuses': appointment_statuses,
        'completed_appointments': completed_appointments,
        'confirmed_appointments': confirmed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'top_doctors': top_doctors,
        'appointments_last_week': appointments_last_week,
        'new_registrations_this_month': new_registrations_this_month,
    }
    return render(request, 'admin/analytics.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin_role)
def export_analytics_csv(request):
    from appointments.models import Appointment
    from django.db.models import Count
    
    # Prepare response with CSV formatting
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics_report.csv"'
    
    writer = csv.writer(response)
    
    # Get all data
    total_patients = User.objects.filter(role='PATIENT').count()
    total_doctors = User.objects.filter(role='DOCTOR').count()
    total_appointments = Appointment.objects.count()
    total_receptionists = User.objects.filter(role='RECEPTIONIST').count()
    
    completed_appointments = Appointment.objects.filter(status='COMPLETED').count()
    confirmed_appointments = Appointment.objects.filter(status='CONFIRMED').count()
    cancelled_appointments = Appointment.objects.filter(status='CANCELLED').count()
    
    last_7_days = timezone.now() - timedelta(days=7)
    appointments_last_week = Appointment.objects.filter(
        appointment_date__gte=last_7_days.date()
    ).count()
    
    this_month = timezone.now()
    new_registrations_this_month = User.objects.filter(
        role='PATIENT',
        date_joined__month=this_month.month,
        date_joined__year=this_month.year
    ).count()
    
    top_doctors = User.objects.filter(role='DOCTOR').annotate(
        appointment_count=Count('appointments_as_doctor')
    ).order_by('-appointment_count')[:5]
    
    # Summary Section
    writer.writerow(['CLINIC ANALYTICS REPORT'])
    writer.writerow([f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])
    
    # System Overview
    writer.writerow(['SYSTEM OVERVIEW'])
    writer.writerow(['Metric', 'Count'])
    writer.writerow(['Total Patients', total_patients])
    writer.writerow(['Total Doctors', total_doctors])
    writer.writerow(['Total Receptionists', total_receptionists])
    writer.writerow(['Total Appointments', total_appointments])
    writer.writerow([])
    
    # Appointment Status
    writer.writerow(['APPOINTMENT STATUS'])
    writer.writerow(['Status', 'Count'])
    writer.writerow(['Completed', completed_appointments])
    writer.writerow(['Confirmed', confirmed_appointments])
    writer.writerow(['Cancelled', cancelled_appointments])
    writer.writerow([])
    
    # Performance Metrics
    writer.writerow(['PERFORMANCE METRICS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Appointments Last 7 Days', appointments_last_week])
    writer.writerow(['New Patient Registrations (This Month)', new_registrations_this_month])
    if total_appointments > 0:
        completion_rate = (completed_appointments / total_appointments) * 100
        writer.writerow(['Completion Rate (%)', f'{completion_rate:.2f}'])
    if total_doctors > 0:
        patients_per_doctor = total_patients / total_doctors
        writer.writerow(['Average Patients per Doctor', f'{patients_per_doctor:.2f}'])
    writer.writerow([])
    
    # Top Doctors
    writer.writerow(['TOP DOCTORS'])
    writer.writerow(['Doctor Name', 'Specialization', 'Experience (Years)', 'Appointments'])
    for doctor in top_doctors:
        doctor_profile = DoctorProfile.objects.filter(user=doctor).first()
        specialization = doctor_profile.specialization if doctor_profile else 'N/A'
        experience = doctor_profile.experience_years if doctor_profile else 'N/A'
        writer.writerow([
            f'{doctor.first_name} {doctor.last_name}',
            specialization,
            experience,
            doctor.appointment_count
        ])
    
    return response
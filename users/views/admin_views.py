from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..decorators import is_admin_role
from users.models import User, DoctorProfile

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
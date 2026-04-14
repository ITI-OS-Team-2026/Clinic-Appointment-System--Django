from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import User, PatientProfile

def patient_register(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        e = request.POST.get('email')

        dob = request.POST.get('date_of_birth')
        blood = request.POST.get('blood_type')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        phone = request.POST.get('contact_number')

        full_name = request.POST.get('first_name', '')
        first_name = full_name.split()[0] if full_name else ''
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''

        user = User.objects.create_user(username=u, email=e, password=p, role='PATIENT', first_name=first_name, last_name=last_name)

        PatientProfile.objects.create(
            user=user,
            date_of_birth=dob,
            blood_type=blood,
            gender=gender,
            address=address,
            contact_number=phone
        )

        login(request, user)
        return redirect_based_on_role(request)

    return render(request, 'auth/register.html')

def login_view(request):

    if request.user.is_authenticated:
        return redirect_based_on_role(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_based_on_role(request)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def redirect_based_on_role(request):

    user = request.user
    if user.role == 'PATIENT':
        return redirect('patient_dashboard')
    elif user.role == 'DOCTOR':
        return redirect('doctor_queue')
    elif user.role == 'RECEPTIONIST':
        return redirect('receptionist_queue')
    elif user.role == 'ADMIN':
        return redirect('admin_dashboard')
    else:
        logout(request)
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')

def forget_password(request):
    return render(request, 'auth/forget_password.html')

from django.contrib.auth.decorators import login_required

@login_required(login_url='/users/login/')
def patient_profile(request):
    if request.user.role != 'PATIENT':
        return redirect_based_on_role(request)

    profile = request.user.patient_profile

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.save()

        profile.contact_number = request.POST.get('contact_number', profile.contact_number)
        profile.address = request.POST.get('address', profile.address)
        profile.blood_type = request.POST.get('blood_type', profile.blood_type)
        profile.gender = request.POST.get('gender', profile.gender)

        dob = request.POST.get('date_of_birth')
        if dob:
            profile.date_of_birth = dob

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_profile')

    return render(request, 'patient/profile.html', {'profile': profile})
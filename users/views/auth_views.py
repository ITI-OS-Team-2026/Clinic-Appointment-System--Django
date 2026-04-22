from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import User, PatientProfile

def patient_register(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request)

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        cp = request.POST.get('confirm_password', '').strip()
        e = request.POST.get('email', '').strip()

        dob = request.POST.get('date_of_birth')
        blood = request.POST.get('blood_type')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        phone = request.POST.get('contact_number')

        full_name = request.POST.get('first_name', '').strip()
        first_name = full_name.split()[0] if full_name else ''
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''

        has_error = False

        if not u:
            messages.error(request, 'Username is required.')
            has_error = True

        elif User.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists. Please choose a different one.')
            has_error = True

        if not e:
            messages.error(request, 'Email is required.')
            has_error = True
        elif User.objects.filter(email=e).exists():
            messages.error(request, 'Email already registered. Please use a different email or log in.')
            has_error = True

        if not p:
            messages.error(request, 'Password is required.')
            has_error = True
        elif len(p) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            has_error = True

        if p != cp:
            messages.error(request, 'Passwords do not match.')
            has_error = True

        if not dob:
            messages.error(request, 'Date of birth is required.')
            has_error = True

        if has_error:
            return render(request, 'auth/register.html')

        try:
            user = User.objects.create_user(username=u, email=e, password=p, role='PATIENT', first_name=first_name, last_name=last_name)

            PatientProfile.objects.create(
                user=user,
                date_of_birth=dob,
                blood_type=blood,
                gender=gender,
                address=address,
                contact_number=phone
            )
            
            messages.success(request, 'Account created successfully! You are now logged in.')
            login(request, user)
            return redirect_based_on_role(request)
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'auth/register.html')

    return render(request, 'auth/register.html')

def login_view(request):

    if request.user.is_authenticated:
        return redirect_based_on_role(request)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'auth/login.html')

        if not password:
            messages.error(request, 'Password is required.')
            return render(request, 'auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect_based_on_role(request)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, 'auth/login.html')
    
    return render(request, 'auth/login.html')

def redirect_based_on_role(request):

    user = request.user
    if user.role == 'PATIENT':
        return redirect('patient_dashboard')
    elif user.role == 'DOCTOR':
        return redirect('doctor_queue')
    elif user.role == 'RECEPTIONIST':
        return redirect('receptionist_queue')
    elif user.role == 'ADMIN' or user.is_superuser:
        return redirect('admin_dashboard')
    else:
        logout(request)
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'auth/forget_password.html')

        try:
            user = User.objects.get(email=email)
 
            messages.success(request, f'If an account with {email} exists, you will receive an email with password reset instructions.')
            return render(request, 'auth/forget_password.html')
        except User.DoesNotExist:

            messages.success(request, f'If an account with {email} exists, you will receive an email with password reset instructions.')
            return render(request, 'auth/forget_password.html')

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
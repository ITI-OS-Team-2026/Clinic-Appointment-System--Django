import re

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from users.models import User, PatientProfile

def landing(request):
    return render(request, 'landing.html')

def patient_register(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request)

    if request.method == 'POST':
        from datetime import datetime, date

        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        cp = request.POST.get('confirm_password', '').strip()
        e = request.POST.get('email', '').strip()

        dob = request.POST.get('date_of_birth', '').strip()
        blood = request.POST.get('blood_type', '').strip()
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('contact_number', '').strip()

        full_name = request.POST.get('first_name', '').strip()
        first_name = full_name.split()[0] if full_name else ''
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''

        form_data = {
            'username': u,
            'email': e,
            'date_of_birth': dob,
            'blood_type': blood,
            'gender': gender,
            'address': address,
            'contact_number': phone,
            'first_name': full_name,
        }

        field_errors = {}
        has_error = False

        if (
            not full_name
            or len(full_name.split()) < 2
            or not re.match(r'^[a-zA-Z\s]+$', full_name)
        ):
            field_errors['full_name'] = 'Name must contain letters only, no numbers or special characters'
            has_error = True

        if not u or not re.match(r'^[a-zA-Z0-9_]+$', u):
            field_errors['username'] = 'Username cannot contain spaces or special characters'
            has_error = True
        elif User.objects.filter(username=u).exists():
            field_errors['username'] = 'Username already exists'
            has_error = True

        if not e or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', e):
            field_errors['email'] = 'Please enter a valid email'
            has_error = True
        elif User.objects.filter(email=e).exists():
            field_errors['email'] = 'Email already exists'
            has_error = True

        dob_date = None
        if not dob:
            field_errors['date_of_birth'] = 'Date of birth is required'
            has_error = True
        else:
            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                field_errors['date_of_birth'] = 'Invalid date format'
                has_error = True

        if dob_date:
            today = date.today()
            if dob_date > today:
                field_errors['date_of_birth'] = 'Date of birth cannot be in the future'
                has_error = True

        if not gender:
            field_errors['gender'] = 'Please select a gender'
            has_error = True

        if not blood:
            field_errors['blood_type'] = 'Please select a blood type'
            has_error = True

        if not phone or not re.match(r'^\+?\d+$', phone):
            field_errors['contact_number'] = 'Phone number must contain numbers only, + is only allowed at the start'
            has_error = True

        if not address:
            field_errors['address'] = 'Address is required'
            has_error = True

        if not p or not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#]).{8,}$', p):
            field_errors['password'] = 'Password must be at least 8 characters with uppercase, lowercase, number, and special character (@$!%*?&#)'
            has_error = True

        if p != cp:
            field_errors['confirm_password'] = 'Passwords do not match'
            has_error = True

        if has_error:
            for error_message in field_errors.values():
                messages.error(request, error_message)
            return render(request, 'auth/register.html', {'form_data': form_data, 'field_errors': field_errors})

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=u, email=e, password=p, role='PATIENT', first_name=first_name, last_name=last_name)

                PatientProfile.objects.create(
                    user=user,
                    date_of_birth=dob,
                    blood_type=blood,
                    gender=gender,
                    address=address,
                    contact_number=phone
                )
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'auth/register.html', {'form_data': form_data})

        messages.success(request, 'Account created successfully! You are now logged in.')
        login(request, user)
        return redirect_based_on_role(request)

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
    elif user.role == 'ADMIN':
        return redirect('admin_dashboard')
    else:
        logout(request)
        return redirect('login')

def logout_view(request):
    # Clear all messages safely so they don't persist
    list(messages.get_messages(request))
    
    # Logout user
    logout(request)
    
    # Flush session
    request.session.flush()
    
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

def edit_patient_profile(request, profile):
    from datetime import datetime, date
    errors = []

    # Get values from POST
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    contact_number = request.POST.get('contact_number', '').strip()
    address = request.POST.get('address', '').strip()
    blood_type = request.POST.get('blood_type', '').strip()
    gender = request.POST.get('gender', '').strip()
    dob = request.POST.get('date_of_birth', '').strip()

    # PHASE 1: Validate only
    if not first_name:
        errors.append('First name cannot be empty')
    elif not re.match(r'^[a-zA-Z\s]+$', first_name):
        errors.append('First name must contain letters only')

    if not last_name:
        errors.append('Last name cannot be empty')
    elif not re.match(r'^[a-zA-Z\s]+$', last_name):
        errors.append('Last name must contain letters only')

    if not contact_number:
        errors.append('Contact number cannot be empty')
    elif not re.match(r'^\+?\d+$', contact_number):
        errors.append('Phone number must contain numbers only')

    if not address:
        errors.append('Address cannot be empty')

    dob_date = None
    if dob:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            if dob_date > date.today():
                errors.append('Date of birth cannot be in the future')
        except ValueError:
            errors.append('Invalid date format')

    if errors:
        return False, errors

    # PHASE 2: Update object only after validation passes
    profile.user.first_name = first_name
    profile.user.last_name = last_name
    profile.contact_number = contact_number
    profile.address = address
    if blood_type:
        profile.blood_type = blood_type
    if gender:
        profile.gender = gender
    if dob_date:
        profile.date_of_birth = dob_date

    with transaction.atomic():
        profile.user.save()
        profile.save()

    return True, []

@login_required(login_url='/users/login/')
def patient_profile(request):
    if request.user.role != 'PATIENT':
        return redirect_based_on_role(request)

    profile = request.user.patient_profile

    if request.method == 'POST':
        success, errors = edit_patient_profile(request, profile)
        if success:
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')
        else:
            for error_message in errors:
                messages.error(request, error_message)
            return render(request, 'patient/profile.html', {
                'profile': profile,
                'edit_mode': True
            })

    return render(request, 'patient/profile.html', {'profile': profile})
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

        user = User.objects.create_user(username=u, email=e, password=p, role='PATIENT')
        
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

    return render(request, 'register.html')


def login_view(request):
    
    # If they are already logged in, don't let them see the login page
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect_based_on_role(user)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def redirect_based_on_role(user):
    if user.role == 'PATIENT':
        return redirect('patient_dashboard')
    elif user.role == 'DOCTOR':
        return redirect('doctor_queue')
    elif user.role == 'RECEPTIONIST':
        return redirect('receptionist_queue')
    elif user.role == 'ADMIN':
        return redirect('admin_dashboard')
    else:
        logout(user)
        return redirect('login')
    

def logout_view(request):
    logout(request)
    return redirect('login')
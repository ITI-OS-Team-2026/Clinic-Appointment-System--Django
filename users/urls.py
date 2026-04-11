from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)

from users.views.admin_views import add_doctor, admin_dashboard
from .views.auth_views import login_view, logout_view, patient_register, forget_password

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', patient_register, name='register'),
    path('forget-password/', PasswordResetView.as_view(template_name='auth/forget_password.html'), name='password_reset'),
    path('forget-password/done/', PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('forget-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('forget-password/complete/', PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/add-doctor/', add_doctor, name='add_doctor'),
]
from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from users.views.admin_views import activate_user, add_doctor, add_receptionist, admin_dashboard, analytics, deactivate_user, export_analytics_csv, user_detail, user_management
from .views.auth_views import login_view, logout_view, patient_register, forget_password, patient_profile

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', patient_register, name='register'),
    path('patient/profile/', patient_profile, name='patient_profile'),
    path('forget-password/', PasswordResetView.as_view(template_name='auth/forget_password.html'), name='password_reset'),
    path('forget-password/done/', PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('forget-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('forget-password/complete/', PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', user_management, name='user_management'),
    path('admin-dashboard/users/<int:user_id>/', user_detail, name='user_detail'),
    path('admin-dashboard/users/<int:user_id>/deactivate/', deactivate_user, name='deactivate_user'),
    path('admin-dashboard/users/<int:user_id>/activate/', activate_user, name='activate_user'),
    path('admin-dashboard/add-doctor/', add_doctor, name='add_doctor'),
    path('admin-dashboard/add-receptionist/', add_receptionist, name='add_receptionist'),
    path('admin-dashboard/analytics/', analytics, name='analytics'),
    path('admin-dashboard/analytics/export/', export_analytics_csv, name='export_analytics_csv'),
]
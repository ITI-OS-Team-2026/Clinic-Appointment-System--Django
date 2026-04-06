from django.urls import path

from users.views.admin_views import admin_dashboard
from .views.auth_views import login_view, logout_view, patient_register

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', patient_register, name='register'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]
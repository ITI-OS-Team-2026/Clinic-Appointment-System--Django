from django.urls import path

from users.views.admin_views import admin_dashboard
from .views.auth_views import login_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]
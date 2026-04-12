from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('patients/', include('patients.urls')),
    path('users/', include('users.urls')),
    path('appointments/', include('appointments.urls')),
    path('records/', include('records.urls')),
    path('', TemplateView.as_view(template_name="base.html"), name="home"),
    path("__reload__/", include("django_browser_reload.urls")),
    path('api/', include('availabilitySlots.urls')),
]

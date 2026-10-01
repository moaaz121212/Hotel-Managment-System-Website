# luxe_hotel/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotel.urls', namespace='hotel')),  # Hotel app URLs with namespace
    path('accounts/', include('django.contrib.auth.urls')),  # Django auth URLs (login, etc.)
    path('login/', auth_views.LoginView.as_view(template_name='hotel/login.html'), name='login'),  # Custom login template
]
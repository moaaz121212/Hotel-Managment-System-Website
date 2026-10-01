# hotel/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'hotel'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('rooms/', views.RoomList.as_view(), name='room_list'),
    path('bookings/', views.BookingView.as_view(), name='bookings'),
    path('booking-list/', views.BookingList.as_view(), name='booking_list'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('logout/', auth_views.LogoutView.as_view(next_page='hotel:home'), name='logout'),
    path('send-confirmation/', views.send_confirmation, name='send_confirmation')
]
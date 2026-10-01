from django.views.generic import ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from hotel.models import Room, Booking
from .forms import UserRegisterForm, BookingForm, PaymentForm
from django.utils import timezone
from hotel.utils.email_utils import send_booking_confirmation_email
from django.http import HttpResponse

def home(request):
    return render(request, 'hotel/home.html', {})

def contact(request):
    return render(request, 'hotel/contact.html', {})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('hotel:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'hotel/register.html', {'form': form})

class RoomList(ListView):
    model = Room
    template_name = 'hotel/room_list.html'
    context_object_name = 'rooms'

class BookingList(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'hotel/booking_list.html'
    context_object_name = 'bookings'
    login_url = '/login/'
    redirect_field_name = 'next'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingView(View):
    template_name = 'hotel/bookings.html'

    def get(self, request):
        form = BookingForm()
        return render(request, self.template_name, {
            'form': form,
            'is_authenticated': request.user.is_authenticated
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {
                'form': BookingForm(),
                'is_authenticated': False,
                'error': 'Please log in to make a booking.'
            })

        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.special_requests = request.POST.get('special-requests', '')
            booking.payment_status = 'pending'
            duration = (booking.end_date - booking.start_date).days or 1
            booking.total_price = booking.room.price_per_night * duration
            booking.save()
            messages.success(request, 'Booking created successfully! Proceed to payment.')
            return redirect('hotel:payment', booking_id=booking.id)
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, self.template_name, {
            'form': form,
            'is_authenticated': True
        })

def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to cancel a booking.")
        return redirect('login')
    
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.start_date <= timezone.now():
        messages.error(request, "Cannot cancel a booking that has already started.")
        return redirect('hotel:booking_list')
    
    if request.method == "POST":
        booking.delete()
        messages.success(request, f"Booking ID {booking_id} cancelled successfully.")
        return redirect('hotel:booking_list')
    
    return redirect('hotel:booking_list')

def payment(request, booking_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to make a payment.")
        return redirect('login')
    
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    amount = calculate_amount(booking)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            booking.payment_status = 'completed'
            booking.save()
            send_booking_confirmation_email(booking.user.email, booking)  # Pass user email and booking object
            messages.success(request, 'Payment successful! Your booking is confirmed. A confirmation email has been sent.')
            return redirect('hotel:booking_list')
    else:
        form = PaymentForm()
    
    return render(request, 'hotel/payment.html', {
        'form': form,
        'booking_id': booking_id,
        'amount': amount,
    })

def calculate_amount(booking):
    room = booking.room
    duration = (booking.end_date - booking.start_date).days or 1
    return room.price_per_night * duration

def send_confirmation(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Please provide a valid email address.")
            return redirect('hotel:checkout')  # Adjust to your checkout URL

        # Fetch the latest booking for the user (assuming one active booking per session)
        booking = Booking.objects.filter(user=request.user).order_by('-id').first()
        if not booking:
            messages.error(request, "No booking found to confirm.")
            return redirect('hotel:checkout')

        try:
            send_booking_confirmation_email(email, booking)
            messages.success(request, f"Confirmation sent to {email}")
        except Exception as e:
            messages.error(request, f"Failed to send email: {e}")

        return redirect('hotel:checkout_success')  # Adjust to your success URL
    return redirect('hotel:checkout')  # Adjust to your checkout URL

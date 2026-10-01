from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_booking_confirmation_email(email, booking):
    """
    Send a booking confirmation email to the specified email address.
    
    Args:
        email (str): The recipient's email address.
        booking (Booking): The booking object containing the reservation details.
    """
    user = {
        'username': booking.user.username,
        'first_name': booking.user.first_name or booking.user.username,
        'email': email,
    }
    booking_data = {
        'reference': getattr(booking, 'reference', booking.id),  # Fallback to id if reference doesn't exist
        'checkin_date': booking.start_date.strftime('%Y-%m-%d'),
        'checkout_date': booking.end_date.strftime('%Y-%m-%d'),
        'room_category': getattr(booking.room, 'category', 'Standard'),  # Adjust if room category field differs
        'guests': booking.guests or 1,
        'total_amount': f"${booking.total_price:.2f}",
        'special_requests': booking.special_requests or 'None',
    }

    html_message = render_to_string('emails/booking_confirmation.html', {
        'user': user,
        'booking': booking_data,
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]

    send_mail(
        subject='Booking Confirmation - Luxe Hotel',
        message=plain_message,
        from_email=from_email,
        recipient_list=to_email,
        html_message=html_message,
        fail_silently=False,
    )
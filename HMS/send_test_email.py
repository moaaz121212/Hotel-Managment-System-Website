import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HMS.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

recipient = os.environ.get('TEST_EMAIL_RECIPIENT')
if not recipient:
    raise RuntimeError('Set TEST_EMAIL_RECIPIENT to an address before sending a test email.')

test_user = {
    'username': 'test-user',
    'first_name': 'Guest',
    'email': recipient,
}
test_booking = {
    'reference': 'BOOK-123456',
    'checkin_date': '2025-05-20',
    'checkout_date': '2025-05-22',
    'room_category': 'LUXURY',
    'guests': 2,
    'total_amount': '$300',
    'special_requests': 'Early check-in preferred',
}

html_message = render_to_string('emails/booking_confirmation.html', {
    'user': test_user,
    'booking': test_booking,
})
plain_message = strip_tags(html_message)

send_mail(
    'Test Booking Confirmation - Luxe Hotel',
    plain_message,
    settings.DEFAULT_FROM_EMAIL,
    [recipient],
    html_message=html_message,
    fail_silently=False,
)
print(f'Test email sent to {recipient}.')
from hotel.models import Booking

def check_availability(room, check_in, check_out):
    """
    Check if a room is available for the given date range.
    """
    bookings = Booking.objects.filter(room=room)
    for booking in bookings:
        if check_in < booking.end_date and check_out > booking.start_date:
            return False
    return True
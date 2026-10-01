from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    number = models.CharField(max_length=10)
    category = models.CharField(max_length=20, choices=[
        ('YES', 'AC'),
        ('NON', 'NON-AC'),
        ('LUX', 'LUXURY'),
        ('DEL', 'DELUXE'),
        ('KIN', 'KING'),
        ('QUE', 'QUEEN'),
    ])
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # Added for pricing

    def __str__(self):
        return self.number

    def get_category_display(self):
        return dict(self._meta.get_field('category').choices).get(self.category, self.category)

class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    guests = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')  # Added for payment tracking
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Booking {self.id} for {self.user.username}"

    @property
    def calculate_total_price(self):
        # Example calculation, adjust as needed:
        if self.start_date and self.end_date and self.room and hasattr(self.room, 'price_per_night'):
            nights = (self.end_date - self.start_date).days
            return nights * self.room.price_per_night
        return 0
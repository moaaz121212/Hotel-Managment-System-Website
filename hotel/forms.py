from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Room
from django.utils import timezone
import re

class BookingForm(forms.ModelForm):
    rooms_category = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        label="Room",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'aria-describedby': 'roomHelp'})
    )
    check_in = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'aria-describedby': 'startDateHelp',
            'step': '300',  # 5-minute intervals
        })
    )
    check_out = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'aria-describedby': 'endDateHelp',
            'step': '300',  # 5-minute intervals
        })
    )
    guests = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'aria-describedby': 'guestsHelp'})
    )

    class Meta:
        model = Booking
        fields = ['rooms_category', 'check_in', 'check_out', 'guests']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically filter available rooms
        if self.data.get('check_in') and self.data.get('check_out'):
            try:
                check_in = timezone.datetime.fromisoformat(self.data['check_in'].replace('T', ' '))
                check_out = timezone.datetime.fromisoformat(self.data['check_out'].replace('T', ' '))
                booked_rooms = Booking.objects.filter(
                    start_date__lt=check_out,
                    end_date__gt=check_in
                ).values('room').distinct()
                available_rooms = Room.objects.exclude(id__in=booked_rooms)
                self.fields['rooms_category'].queryset = available_rooms
            except ValueError:
                self.fields['rooms_category'].queryset = Room.objects.all()
        else:
            self.fields['rooms_category'].queryset = Room.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        room = cleaned_data.get('rooms_category')

        # Ensure check_in is not in the past
        if check_in and check_in < timezone.now():
            raise forms.ValidationError("Check-in date cannot be in the past.")

        # Ensure check_out is after check_in
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out date must be after check-in date.")

        # Check room availability
        if room and check_in and check_out:
            overlapping_bookings = Booking.objects.filter(
                room=room,
                start_date__lt=check_out,
                end_date__gt=check_in
            ).exclude(id=self.instance.id if self.instance else None)
            if overlapping_bookings.exists():
                raise forms.ValidationError("Selected room is not available for the chosen dates.")

        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.room = self.cleaned_data['rooms_category']
        booking.start_date = self.cleaned_data['check_in']
        booking.end_date = self.cleaned_data['check_out']
        booking.guests = self.cleaned_data['guests']
        if commit:
            booking.save()
        return booking

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class PaymentForm(forms.Form):
    cardholder_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Doe',
            'id': 'cardholder_name',
            'aria-describedby': 'cardholderNameHelp'
        })
    )
    card_number = forms.CharField(
        max_length=19,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'id': 'card_number',
            'aria-describedby': 'cardNumberHelp'
        })
    )
    expiry_date = forms.CharField(
        max_length=5,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'id': 'expiry_date',
            'aria-describedby': 'expiryDateHelp'
        })
    )
    cvv = forms.CharField(
        max_length=4,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'id': 'cvv',
            'aria-describedby': 'cvvHelp'
        })
    )

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number'].replace(' ', '')
        if not re.match(r'^\d{16}$', card_number):
            raise forms.ValidationError("Card number must be 16 digits.")
        return card_number

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if not re.match(r'^(0[1-9]|1[0-2])\/[0-9]{2}$', expiry_date):
            raise forms.ValidationError("Expiry date must be in MM/YY format.")
        month, year = map(int, expiry_date.split('/'))
        current_year = timezone.now().year % 100
        current_month = timezone.now().month
        if year < current_year or (year == current_year and month < current_month):
            raise forms.ValidationError("Card has expired.")
        return expiry_date

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not re.match(r'^\d{3,4}$', cvv):
            raise forms.ValidationError("CVV must be 3 or 4 digits.")
        return cvv
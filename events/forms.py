from django import forms
from django.contrib.auth.models import User
from .models import Event, TicketTier, Booking, UserProfile, Category

class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('attendee', 'Attendee (Discover & Book Events)'),
        ('organizer', 'Organizer (Create & Host Events)'),
    )

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial='attendee', widget=forms.RadioSelect(attrs={'class': 'btn-check'}))
    organization_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company / Organization name'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': True}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['organization_name', 'phone', 'website', 'avatar_url', 'bio']
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acme Events Inc.'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourwebsite.com'}),
            'avatar_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/... or leave blank'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself or your organization...'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'category', 'short_description', 'description',
            'banner_url', 'banner_image', 'format', 'venue_name', 'address', 'city',
            'online_meeting_url', 'start_date', 'end_date', 'status',
            'is_featured', 'tags', 'agenda', 'speakers', 'faqs'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Global AI & Tech Summit 2026'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'A catchy brief hook about the event (max 300 chars)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Detailed description of the event, highlights, and why attendees should join...'}),
            'banner_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/... (High-res banner URL)'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-select'}),
            'venue_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grand Convention Center or Zoom Platform'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Innovation Blvd'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Francisco, CA'}),
            'online_meeting_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/j/123456789 (if online/hybrid)'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AI, Machine Learning, Web3, Networking'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control font-monospace small', 'rows': 4, 'placeholder': '09:00 AM | Registration & Breakfast | Welcome coffee\n10:00 AM | Keynote Address | Future of AI'}),
            'speakers': forms.Textarea(attrs={'class': 'form-control font-monospace small', 'rows': 4, 'placeholder': 'Dr. Elena Vance | Chief AI Scientist at DeepMind\nAlex Rivera | VP of Engineering at CloudScale'}),
            'faqs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Q: Are refunds allowed? A: Full refund up to 7 days before.'}),
        }


class TicketTierForm(forms.ModelForm):
    class Meta:
        model = TicketTier
        fields = ['name', 'description', 'price', 'capacity', 'perks', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. General Admission / VIP Pass'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'perks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Priority Seating, Free Swag, Lunch Included'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BookingCheckoutForm(forms.Form):
    attendee_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    attendee_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    attendee_phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    ticket_tier_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, max_value=10, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control text-center', 'min': '1', 'max': '10'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Special requirements or dietary preferences...'}))
    payment_method = forms.CharField(required=False, initial='Credit Card (Demo)', widget=forms.HiddenInput())


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-calendar-event (Bootstrap icon)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Category description'}),
        }

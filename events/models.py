import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('attendee', 'Attendee'),
        ('organizer', 'Event Organizer'),
        ('admin', 'Platform Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    phone = models.CharField(max_length=25, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, default='')
    organization_name = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def display_avatar(self):
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        # Clean SVG-style UI avatar placeholder
        name = self.user.get_full_name() or self.user.username
        return f"https://ui-avatars.com/api/?name={name}&background=7c3aed&color=fff&size=128&bold=true"

    @property
    def is_organizer(self):
        return self.role in ['organizer', 'admin'] or self.user.is_staff or self.user.is_superuser

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff or self.user.is_superuser


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-calendar-event', help_text='Bootstrap Icon class')
    color_gradient = models.CharField(max_length=100, default='from-purple-600 to-indigo-600')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def event_count(self):
        return self.events.filter(status='published').count()


class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    FORMAT_CHOICES = (
        ('in_person', 'In-Person'),
        ('online', 'Online / Virtual'),
        ('hybrid', 'Hybrid'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    
    banner_image = models.ImageField(upload_to='events/banners/', blank=True, null=True)
    banner_url = models.URLField(blank=True, default='')

    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='in_person')
    venue_name = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    online_meeting_url = models.URLField(blank=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_featured = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')

    # Agenda, Speakers, FAQs stored as text/json
    agenda = models.TextField(blank=True, help_text='Pipe or newline-delimited agenda items')
    speakers = models.TextField(blank=True, help_text='Pipe or newline-delimited speakers')
    faqs = models.TextField(blank=True, help_text='Q&A text')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "event"
            unique_slug = base_slug
            counter = 1
            while Event.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def display_banner(self):
        if self.banner_image:
            return self.banner_image.url
        if self.banner_url:
            return self.banner_url
        # Premium unsplash fallback
        return "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80"

    @property
    def min_price(self):
        tiers = self.ticket_tiers.filter(is_active=True)
        if not tiers.exists():
            return 0.0
        return min(tier.price for tier in tiers)

    @property
    def is_free(self):
        return self.min_price == 0

    @property
    def total_capacity(self):
        return sum(tier.capacity for tier in self.ticket_tiers.filter(is_active=True))

    @property
    def total_tickets_sold(self):
        return sum(tier.tickets_sold for tier in self.ticket_tiers.all())

    @property
    def spots_left(self):
        return max(0, self.total_capacity - self.total_tickets_sold)

    @property
    def is_sold_out(self):
        return self.total_capacity > 0 and self.spots_left <= 0

    @property
    def is_upcoming(self):
        return self.end_date >= timezone.now()

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def parsed_speakers(self):
        """Returns list of speaker dicts: [{'name': '...', 'role': '...'}]"""
        if not self.speakers:
            return []
        speakers_list = []
        for line in self.speakers.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            name = parts[0].strip()
            role = parts[1].strip() if len(parts) > 1 else 'Keynote Speaker'
            speakers_list.append({'name': name, 'role': role})
        return speakers_list

    @property
    def parsed_agenda(self):
        """Returns list of agenda dicts: [{'time': '...', 'title': '...', 'desc': '...'}]"""
        if not self.agenda:
            return []
        agenda_list = []
        for line in self.agenda.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            time_str = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else ''
            desc = parts[2].strip() if len(parts) > 2 else ''
            agenda_list.append({'time': time_str, 'title': title, 'desc': desc})
        return agenda_list


class TicketTier(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_tiers')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    capacity = models.PositiveIntegerField(default=100)
    tickets_sold = models.PositiveIntegerField(default=0)
    perks = models.TextField(blank=True, help_text='Comma-separated perks')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event.title} - {self.name} (${self.price})"

    @property
    def available_quantity(self):
        return max(0, self.capacity - self.tickets_sold)

    @property
    def perk_list(self):
        if not self.perks:
            return []
        return [p.strip() for p in self.perks.split(',') if p.strip()]


class Booking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('free', 'Free Pass'),
        ('pending', 'Pending'),
    )

    booking_reference = models.CharField(max_length=24, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='paid')
    payment_method = models.CharField(max_length=50, default='Credit Card (Demo)')

    attendee_name = models.CharField(max_length=150)
    attendee_email = models.EmailField()
    attendee_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)

    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booked_at']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference} - {self.attendee_name} ({self.event.title})"

    @property
    def total_tickets(self):
        return sum(item.quantity for item in self.items.all())


class TicketItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    ticket_tier = models.ForeignKey(TicketTier, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    qr_code_token = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_token:
            self.qr_code_token = f"TKT-{uuid.uuid4().hex.upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_tier.name} x {self.quantity} for {self.booking.booking_reference}"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('booking_confirmed', 'Booking Confirmed'),
        ('ticket_sold', 'Ticket Sold'),
        ('event_reminder', 'Event Reminder'),
        ('event_update', 'Event Update'),
        ('system', 'System Alert'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class SavedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='saves')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved {self.event.title}"

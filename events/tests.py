from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Category, Event, TicketTier, Booking, TicketItem, Notification, SavedEvent, UserProfile

class EventPlatformTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        UserProfile.objects.create(user=self.admin_user, role='admin')

        self.organizer = User.objects.create_user('organizer', 'org@test.com', 'org123')
        UserProfile.objects.create(user=self.organizer, role='organizer', organization_name='Test Org')

        self.attendee = User.objects.create_user('attendee', 'att@test.com', 'att123')
        UserProfile.objects.create(user=self.attendee, role='attendee')

        # Category
        self.category = Category.objects.create(name='Technology', icon='bi-cpu-fill')

        # Event
        now = timezone.now()
        self.event = Event.objects.create(
            title='AI DevCon 2026',
            organizer=self.organizer,
            category=self.category,
            short_description='Test short description',
            description='Test full description',
            format='in_person',
            venue_name='Test Center',
            city='San Francisco',
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=3),
            status='published',
            is_featured=True
        )

        # Ticket Tiers
        self.tier_free = TicketTier.objects.create(
            event=self.event,
            name='Community Free Pass',
            price=Decimal('0.00'),
            capacity=100
        )
        self.tier_paid = TicketTier.objects.create(
            event=self.event,
            name='VIP Pass',
            price=Decimal('99.00'),
            capacity=50
        )

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EventPulse')
        self.assertContains(response, 'AI DevCon 2026')

    def test_search_page(self):
        response = self.client.get('/search/?q=AI')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI DevCon 2026')

    def test_event_detail_page(self):
        response = self.client.get(f'/event/{self.event.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI DevCon 2026')
        self.assertContains(response, 'Community Free Pass')
        self.assertContains(response, 'VIP Pass')

    def test_ticket_booking_flow(self):
        self.client.login(username='attendee', password='att123')
        response = self.client.post(f'/event/{self.event.slug}/book/', {
            'ticket_tier_id': self.tier_paid.id,
            'quantity': 2,
            'attendee_name': 'Test Attendee',
            'attendee_email': 'att@test.com',
            'attendee_phone': '1234567890',
            'notes': 'Gluten free'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.filter(user=self.attendee).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.items.count(), 1)
        self.assertEqual(booking.items.first().quantity, 2)
        # Check tier capacity decremented
        self.tier_paid.refresh_from_db()
        self.assertEqual(self.tier_paid.tickets_sold, 2)
        # Check e-ticket page
        self.assertContains(response, booking.booking_reference)
        self.assertContains(response, 'Official E-Ticket')

    def test_user_dashboard(self):
        self.client.login(username='attendee', password='att123')
        response = self.client.get('/dashboard/user/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Attendee Dashboard')

    def test_organizer_dashboard_and_crud(self):
        self.client.login(username='organizer', password='org123')
        # Dashboard
        response = self.client.get('/dashboard/organizer/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Organizer Hub')

        # Create Event
        now = timezone.now()
        post_data = {
            'title': 'New Workshop 2026',
            'category': self.category.id,
            'short_description': 'A workshop',
            'description': 'Full workshop description',
            'format': 'online',
            'online_meeting_url': 'https://zoom.us/j/12345',
            'start_date': (now + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
            'end_date': (now + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M'),
            'status': 'published',
            'tier_name[]': ['General'],
            'tier_price[]': ['10.00'],
            'tier_capacity[]': ['50'],
            'tier_perks[]': ['Access']
        }
        res_create = self.client.post('/event/new/', post_data, follow=True)
        self.assertEqual(res_create.status_code, 200)
        self.assertTrue(Event.objects.filter(title='New Workshop 2026').exists())

    def test_admin_dashboard(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/dashboard/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Platform Administration')

    def test_reports_analytics(self):
        self.client.login(username='organizer', password='org123')
        response = self.client.get('/dashboard/analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reports & Sales Analytics')

    def test_notifications(self):
        self.client.login(username='attendee', password='att123')
        Notification.objects.create(
            user=self.attendee,
            title='Test Alert',
            message='Your booking is confirmed.',
            notification_type='system'
        )
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Alert')

    def test_csv_exports(self):
        self.client.login(username='organizer', password='org123')
        res1 = self.client.get(f'/event/{self.event.id}/attendees/export/')
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1['Content-Type'], 'text/csv')

        res2 = self.client.get('/dashboard/sales/export/')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2['Content-Type'], 'text/csv')

import csv
import json
from decimal import Decimal
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator

from .models import (
    Event, Category, TicketTier, Booking, TicketItem,
    Notification, SavedEvent, UserProfile
)
from .forms import (
    UserRegistrationForm, UserProfileForm, EventForm,
    TicketTierForm, BookingCheckoutForm, CategoryForm
)


# ==========================================
# 1. HOME & PUBLIC VIEWS
# ==========================================

def home_view(request):
    """Modern Landing Page with Hero, Search, Categories & Featured Events"""
    now = timezone.now()
    
    # KPIs for stats banner
    total_events_count = Event.objects.filter(status='published').count()
    total_attendees_count = User.objects.count() + 150 # realistic base
    total_tickets_sold = Booking.objects.filter(status='confirmed').count() + 420
    
    # Categories with event counts
    categories = Category.objects.annotate(
        pub_count=Count('events', filter=Q(events__status='published'))
    ).order_by('-pub_count')[:8]

    # Featured Events
    featured_events = Event.objects.filter(
        status='published',
        is_featured=True,
        end_date__gte=now
    ).order_by('start_date')[:6]

    # If not enough featured, fill with upcoming
    if featured_events.count() < 3:
        featured_events = Event.objects.filter(
            status='published',
            end_date__gte=now
        ).order_by('start_date')[:6]

    # Upcoming Trending Events
    upcoming_events = Event.objects.filter(
        status='published',
        end_date__gte=now
    ).order_by('start_date')[:8]

    # Online / Virtual Highlights
    online_events = Event.objects.filter(
        status='published',
        format__in=['online', 'hybrid'],
        end_date__gte=now
    ).order_by('start_date')[:4]

    # Saved event IDs for the logged-in user
    saved_event_ids = []
    if request.user.is_authenticated:
        saved_event_ids = list(
            SavedEvent.objects.filter(user=request.user).values_list('event_id', flat=True)
        )

    context = {
        'total_events_count': total_events_count,
        'total_attendees_count': total_attendees_count,
        'total_tickets_sold': total_tickets_sold,
        'categories': categories,
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'online_events': online_events,
        'saved_event_ids': saved_event_ids,
    }
    return render(request, 'home.html', context)


def search_events_view(request):
    """Event Search and Filter by Category, Date, Price, Format and Sorting"""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    event_format = request.GET.get('format', '').strip()
    date_filter = request.GET.get('date', '').strip()
    price_filter = request.GET.get('price', '').strip()
    sort_by = request.GET.get('sort', 'upcoming')

    events = Event.objects.filter(status='published')
    now = timezone.now()

    # Keyword search across title, short_description, venue, city, tags
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(venue_name__icontains=query) |
            Q(city__icontains=query) |
            Q(tags__icontains=query)
        )

    # Category Filter
    if category_slug:
        events = events.filter(category__slug=category_slug)

    # Format Filter
    if event_format and event_format in ['in_person', 'online', 'hybrid']:
        events = events.filter(format=event_format)

    # Date Filter
    if date_filter == 'today':
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        events = events.filter(start_date__gte=today_start, start_date__lt=today_end)
    elif date_filter == 'tomorrow':
        tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_start + timedelta(days=1)
        events = events.filter(start_date__gte=tomorrow_start, start_date__lt=tomorrow_end)
    elif date_filter == 'weekend':
        # Upcoming weekend (Sat/Sun)
        days_ahead = 5 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        sat_start = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0)
        sun_end = sat_start + timedelta(days=2)
        events = events.filter(start_date__gte=sat_start, start_date__lt=sun_end)
    elif date_filter == 'month':
        month_end = (now + timedelta(days=30))
        events = events.filter(start_date__gte=now, start_date__lte=month_end)
    else:
        # Default: show upcoming from now
        events = events.filter(end_date__gte=now)

    # Price Filter
    if price_filter == 'free':
        # Tickets with price 0
        events = events.filter(ticket_tiers__price=0).distinct()
    elif price_filter == 'paid':
        events = events.filter(ticket_tiers__price__gt=0).distinct()

    # Sorting
    if sort_by == 'price_asc':
        events = sorted(events, key=lambda e: e.min_price)
    elif sort_by == 'price_desc':
        events = sorted(events, key=lambda e: e.min_price, reverse=True)
    elif sort_by == 'popular':
        events = sorted(events, key=lambda e: e.total_tickets_sold, reverse=True)
    else: # upcoming
        if isinstance(events, list):
            events = sorted(events, key=lambda e: e.start_date)
        else:
            events = events.order_by('start_date')

    # Pagination
    paginator = Paginator(events, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    saved_event_ids = []
    if request.user.is_authenticated:
        saved_event_ids = list(
            SavedEvent.objects.filter(user=request.user).values_list('event_id', flat=True)
        )

    categories = Category.objects.all().order_by('name')

    context = {
        'events': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'selected_format': event_format,
        'selected_date': date_filter,
        'selected_price': price_filter,
        'selected_sort': sort_by,
        'query': query,
        'total_count': paginator.count,
        'saved_event_ids': saved_event_ids,
    }
    return render(request, 'events/search.html', context)


def event_detail_view(request, slug):
    """Rich Event Details with Ticket Tiers, Organizer Profile, Agenda, and FAQs"""
    event = get_object_or_404(Event, slug=slug)
    ticket_tiers = event.ticket_tiers.filter(is_active=True).order_by('price')
    
    # Related events in same category
    related_events = Event.objects.filter(
        category=event.category,
        status='published',
        end_date__gte=timezone.now()
    ).exclude(id=event.id)[:3]

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedEvent.objects.filter(user=request.user, event=event).exists()

    # Booking form
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'attendee_name': request.user.get_full_name() or request.user.username,
            'attendee_email': request.user.email,
        }
        if hasattr(request.user, 'profile') and request.user.profile.phone:
            initial_data['attendee_phone'] = request.user.profile.phone

    booking_form = BookingCheckoutForm(initial=initial_data)

    context = {
        'event': event,
        'ticket_tiers': ticket_tiers,
        'related_events': related_events,
        'is_saved': is_saved,
        'booking_form': booking_form,
    }
    return render(request, 'events/detail.html', context)


# ==========================================
# 2. TICKET BOOKING & REGISTRATION
# ==========================================

@login_required
def book_ticket_view(request, slug):
    """Process Ticket Booking, decrement capacity, create ticket items & notifications"""
    event = get_object_or_404(Event, slug=slug)

    if request.method == 'POST':
        form = BookingCheckoutForm(request.POST)
        if form.is_valid():
            tier_id = form.cleaned_data['ticket_tier_id']
            quantity = form.cleaned_data['quantity']
            attendee_name = form.cleaned_data['attendee_name']
            attendee_email = form.cleaned_data['attendee_email']
            attendee_phone = form.cleaned_data.get('attendee_phone', '')
            notes = form.cleaned_data.get('notes', '')

            try:
                tier = TicketTier.objects.get(id=tier_id, event=event, is_active=True)
            except TicketTier.DoesNotExist:
                messages.error(request, 'Selected ticket tier does not exist or is inactive.')
                return redirect('event_detail', slug=slug)

            # Check capacity
            if tier.available_quantity < quantity:
                messages.error(request, f'Sorry, only {tier.available_quantity} tickets left in this tier.')
                return redirect('event_detail', slug=slug)

            unit_price = tier.price
            subtotal = unit_price * quantity
            platform_fee = (subtotal * Decimal('0.03')) if subtotal > 0 else Decimal('0.00')
            total_amount = subtotal + platform_fee

            payment_status = 'free' if total_amount == 0 else 'paid'

            # Create Booking
            booking = Booking.objects.create(
                user=request.user,
                event=event,
                total_amount=total_amount,
                status='confirmed',
                payment_status=payment_status,
                payment_method=form.cleaned_data.get('payment_method') or 'Credit Card (Demo)',
                attendee_name=attendee_name,
                attendee_email=attendee_email,
                attendee_phone=attendee_phone,
                notes=notes
            )

            # Create Ticket Item
            TicketItem.objects.create(
                booking=booking,
                ticket_tier=tier,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

            # Update tickets sold
            tier.tickets_sold += quantity
            tier.save()

            # Create Notification for Attendee
            Notification.objects.create(
                user=request.user,
                title='Booking Confirmed!',
                message=f'Your registration for "{event.title}" ({tier.name} x {quantity}) is confirmed. Ref: {booking.booking_reference}',
                notification_type='booking_confirmed',
                link=f'/booking/{booking.booking_reference}/'
            )

            # Create Notification for Organizer
            if event.organizer != request.user:
                Notification.objects.create(
                    user=event.organizer,
                    title='New Ticket Sold!',
                    message=f'{attendee_name} just booked {quantity}x {tier.name} for "{event.title}".',
                    notification_type='ticket_sold',
                    link='/dashboard/organizer/'
                )

            messages.success(request, f'Registration successful! Your tickets are ready.')
            return redirect('ticket_detail', booking_ref=booking.booking_reference)
        else:
            messages.error(request, 'Please check the booking form fields.')
            return redirect('event_detail', slug=slug)

    return redirect('event_detail', slug=slug)


@login_required
def ticket_detail_view(request, booking_ref):
    """Display modern digital e-ticket with simulated QR code and barcode"""
    booking = get_object_or_404(Booking, booking_reference=booking_ref)

    # Permission check: booking owner, event organizer, or admin
    if booking.user != request.user and booking.event.organizer != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this ticket.')
        return redirect('home')

    first_item = booking.items.first()
    qr_token = first_item.qr_code_token if first_item else booking.booking_reference

    context = {
        'booking': booking,
        'item': first_item,
        'qr_token': qr_token,
    }
    return render(request, 'events/ticket_view.html', context)


@login_required
def cancel_booking_view(request, booking_ref):
    """Cancel booking and release ticket tier capacity"""
    booking = get_object_or_404(Booking, booking_reference=booking_ref)

    if booking.user != request.user and booking.event.organizer != request.user and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('home')

    if booking.status == 'cancelled':
        messages.info(request, 'This booking has already been cancelled.')
        return redirect('user_dashboard')

    # Release tickets
    for item in booking.items.all():
        tier = item.ticket_tier
        tier.tickets_sold = max(0, tier.tickets_sold - item.quantity)
        tier.save()

    booking.status = 'cancelled'
    booking.save()

    Notification.objects.create(
        user=booking.user,
        title='Booking Cancelled',
        message=f'Your booking for "{booking.event.title}" has been cancelled.',
        notification_type='system',
        link='/dashboard/user/'
    )

    messages.success(request, f'Booking {booking.booking_reference} has been cancelled.')
    return redirect('user_dashboard')


# ==========================================
# 3. USER DASHBOARD
# ==========================================

@login_required
def user_dashboard_view(request):
    """Attendee Dashboard: My Bookings, Saved Events, Profile, Notifications"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    saved_events = SavedEvent.objects.filter(user=request.user).select_related('event')
    notifications = Notification.objects.filter(user=request.user)[:10]

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            request.user.first_name = profile_form.cleaned_data['first_name']
            request.user.last_name = profile_form.cleaned_data['last_name']
            request.user.email = profile_form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_dashboard')
    else:
        profile_form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    active_bookings = bookings.filter(status='confirmed', event__end_date__gte=timezone.now())
    past_bookings = bookings.filter(Q(status='cancelled') | Q(event__end_date__lt=timezone.now()))

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
        'saved_events': saved_events,
        'notifications': notifications,
        'total_bookings_count': bookings.count(),
        'saved_count': saved_events.count(),
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@login_required
def toggle_bookmark_view(request, event_id):
    """AJAX endpoint to bookmark or unbookmark an event"""
    event = get_object_or_404(Event, id=event_id)
    saved_obj, created = SavedEvent.objects.get_or_create(user=request.user, event=event)
    
    if not created:
        saved_obj.delete()
        saved = False
    else:
        saved = True

    return JsonResponse({'success': True, 'saved': saved})


# ==========================================
# 4. ORGANIZER DASHBOARD & EVENT CRUD
# ==========================================

@login_required
def organizer_dashboard_view(request):
    """Organizer Dashboard with Stats, Event List, Recent Sales, Quick Actions"""
    user_events = Event.objects.filter(organizer=request.user).order_by('-created_at')

    # Organizer KPIs
    total_events = user_events.count()
    published_events = user_events.filter(status='published').count()
    
    # Total tickets sold & revenue across organizer's events
    bookings = Booking.objects.filter(event__organizer=request.user, status='confirmed')
    total_revenue = bookings.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_tickets = sum(b.total_tickets for b in bookings)
    unique_attendees = bookings.values('attendee_email').distinct().count()

    recent_sales = bookings.order_by('-booked_at')[:8]

    context = {
        'user_events': user_events,
        'total_events': total_events,
        'published_events': published_events,
        'total_revenue': total_revenue,
        'total_tickets': total_tickets,
        'unique_attendees': unique_attendees,
        'recent_sales': recent_sales,
    }
    return render(request, 'dashboard/organizer_dashboard.html', context)


@login_required
def create_event_view(request):
    """Create a new event with multiple ticket tiers"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        tier_names = request.POST.getlist('tier_name[]')
        tier_prices = request.POST.getlist('tier_price[]')
        tier_capacities = request.POST.getlist('tier_capacity[]')
        tier_perks = request.POST.getlist('tier_perks[]')

        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            # Create ticket tiers
            if tier_names:
                for i in range(len(tier_names)):
                    name = tier_names[i].strip()
                    if not name:
                        continue
                    price_val = Decimal(tier_prices[i] or '0.00')
                    cap_val = int(tier_capacities[i] or '100')
                    perk_val = tier_perks[i] if i < len(tier_perks) else ''

                    TicketTier.objects.create(
                        event=event,
                        name=name,
                        price=price_val,
                        capacity=cap_val,
                        perks=perk_val,
                        is_active=True
                    )
            else:
                # Default free ticket tier if none submitted
                TicketTier.objects.create(
                    event=event,
                    name='General Admission',
                    price=Decimal('0.00'),
                    capacity=100,
                    perks='Full event access',
                    is_active=True
                )

            # Auto promote user to organizer if currently attendee
            if hasattr(request.user, 'profile') and request.user.profile.role == 'attendee':
                request.user.profile.role = 'organizer'
                request.user.profile.save()

            messages.success(request, f'Event "{event.title}" has been created!')
            return redirect('organizer_dashboard')
        else:
            messages.error(request, 'Please correct the errors in the event form.')
    else:
        # Default start date tomorrow at 9 AM, end date tomorrow at 5 PM
        now = timezone.now()
        tomorrow_start = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        tomorrow_end = (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)

        form = EventForm(initial={
            'start_date': tomorrow_start.strftime('%Y-%m-%dT%H:%M'),
            'end_date': tomorrow_end.strftime('%Y-%m-%dT%H:%M'),
            'format': 'in_person',
            'status': 'published',
            'banner_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80',
        })

    context = {
        'form': form,
        'action_title': 'Create New Event',
        'is_edit': False,
    }
    return render(request, 'dashboard/event_form.html', context)


@login_required
def edit_event_view(request, event_id):
    """Edit an existing event and its ticket tiers"""
    event = get_object_or_404(Event, id=event_id)

    # Permission check
    if event.organizer != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('organizer_dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        tier_names = request.POST.getlist('tier_name[]')
        tier_prices = request.POST.getlist('tier_price[]')
        tier_capacities = request.POST.getlist('tier_capacity[]')
        tier_perks = request.POST.getlist('tier_perks[]')
        tier_ids = request.POST.getlist('tier_id[]')

        if form.is_valid():
            form.save()

            # Process updated ticket tiers
            if tier_names:
                for i in range(len(tier_names)):
                    name = tier_names[i].strip()
                    if not name:
                        continue
                    price_val = Decimal(tier_prices[i] or '0.00')
                    cap_val = int(tier_capacities[i] or '100')
                    perk_val = tier_perks[i] if i < len(tier_perks) else ''
                    tid = tier_ids[i] if i < len(tier_ids) and tier_ids[i] else None

                    if tid:
                        try:
                            tier = TicketTier.objects.get(id=tid, event=event)
                            tier.name = name
                            tier.price = price_val
                            tier.capacity = cap_val
                            tier.perks = perk_val
                            tier.save()
                        except TicketTier.DoesNotExist:
                            pass
                    else:
                        TicketTier.objects.create(
                            event=event,
                            name=name,
                            price=price_val,
                            capacity=cap_val,
                            perks=perk_val,
                            is_active=True
                        )

            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('organizer_dashboard')
        else:
            messages.error(request, 'Please check the form inputs.')
    else:
        form = EventForm(instance=event, initial={
            'start_date': event.start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': event.end_date.strftime('%Y-%m-%dT%H:%M'),
        })

    context = {
        'form': form,
        'event': event,
        'ticket_tiers': event.ticket_tiers.all(),
        'action_title': f'Edit Event: {event.title}',
        'is_edit': True,
    }
    return render(request, 'dashboard/event_form.html', context)


@login_required
def delete_event_view(request, event_id):
    """Delete an event with safety confirmation"""
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('organizer_dashboard')

    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" has been deleted.')
        return redirect('organizer_dashboard')

    return render(request, 'dashboard/confirm_delete.html', {'event': event})


@login_required
def event_attendees_view(request, event_id):
    """View attendees list for a specific event"""
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('organizer_dashboard')

    bookings = Booking.objects.filter(event=event).order_by('-booked_at')

    context = {
        'event': event,
        'bookings': bookings,
    }
    return render(request, 'dashboard/event_attendees.html', context)


@login_required
def export_attendees_csv(request, event_id):
    """Export attendees list to CSV file"""
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user and not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendees_{event.slug}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Booking Ref', 'Attendee Name', 'Email', 'Phone', 'Ticket Tier', 'Quantity', 'Amount', 'Status', 'Date Booked'])

    bookings = Booking.objects.filter(event=event).select_related('user').prefetch_related('items')
    for b in bookings:
        first_item = b.items.first()
        tier_name = first_item.ticket_tier.name if first_item else 'General'
        qty = first_item.quantity if first_item else 1
        writer.writerow([
            b.booking_reference,
            b.attendee_name,
            b.attendee_email,
            b.attendee_phone,
            tier_name,
            qty,
            b.total_amount,
            b.status,
            b.booked_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response


# ==========================================
# 5. ADMIN DASHBOARD
# ==========================================

@login_required
def admin_dashboard_view(request):
    """Platform Admin Dashboard: KPIs, Event Moderation, User Roles, Categories"""
    # Permission: staff or role == 'admin'
    is_admin = request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        messages.error(request, 'Access restricted to Platform Administrators.')
        return redirect('home')

    # Platform KPIs
    total_users_count = User.objects.count()
    total_organizers_count = UserProfile.objects.filter(role__in=['organizer', 'admin']).count()
    total_events_count = Event.objects.count()
    total_bookings = Booking.objects.filter(status='confirmed')
    platform_revenue = total_bookings.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Events table
    all_events = Event.objects.all().select_related('organizer', 'category').order_by('-created_at')
    
    # Users table
    all_users = User.objects.all().select_related('profile').order_by('-date_joined')[:20]

    # Categories list + add category form
    categories = Category.objects.annotate(total_events=Count('events')).order_by('-total_events')
    category_form = CategoryForm()

    if request.method == 'POST' and 'add_category' in request.POST:
        c_form = CategoryForm(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.success(request, 'New category created successfully!')
            return redirect('admin_dashboard')

    context = {
        'total_users_count': total_users_count,
        'total_organizers_count': total_organizers_count,
        'total_events_count': total_events_count,
        'platform_revenue': platform_revenue,
        'all_events': all_events,
        'all_users': all_users,
        'categories': categories,
        'category_form': category_form,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def admin_toggle_event_status(request, event_id):
    """Admin quick toggle to feature or publish/unpublish an event"""
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
        return HttpResponse('Unauthorized', status=401)

    event = get_object_or_404(Event, id=event_id)
    action = request.GET.get('action')

    if action == 'toggle_featured':
        event.is_featured = not event.is_featured
        event.save()
        messages.success(request, f'Event "{event.title}" featured status set to {event.is_featured}.')
    elif action == 'toggle_status':
        event.status = 'draft' if event.status == 'published' else 'published'
        event.save()
        messages.success(request, f'Event "{event.title}" status set to {event.status}.')

    return redirect('admin_dashboard')


@login_required
def admin_toggle_user_role(request, user_id):
    """Admin switcher for user role (attendee <-> organizer)"""
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
        return HttpResponse('Unauthorized', status=401)

    target_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    
    new_role = request.POST.get('new_role') or request.GET.get('role')
    if new_role in ['attendee', 'organizer', 'admin']:
        profile.role = new_role
        profile.save()
        messages.success(request, f'Updated {target_user.username}\'s role to {new_role}.')

    return redirect('admin_dashboard')


# ==========================================
# 6. REPORTS & ANALYTICS
# ==========================================

@login_required
def reports_analytics_view(request):
    """Analytics & Sales Reports with Chart.js: Revenue Trends, Categories, Tiers"""
    is_organizer_or_admin = (
        request.user.is_staff or
        (hasattr(request.user, 'profile') and request.user.profile.is_organizer)
    )
    if not is_organizer_or_admin:
        messages.error(request, 'Access restricted to Organizers and Admins.')
        return redirect('user_dashboard')

    now = timezone.now()

    # Base query: if admin, all events; if organizer, user's events
    if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        events_qs = Event.objects.all()
        bookings_qs = Booking.objects.filter(status='confirmed')
    else:
        events_qs = Event.objects.filter(organizer=request.user)
        bookings_qs = Booking.objects.filter(event__organizer=request.user, status='confirmed')

    total_revenue = bookings_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_tickets = sum(b.total_tickets for b in bookings_qs)
    total_events_count = events_qs.count()

    # 1. Monthly Revenue & Sales Trend (Last 6 Months)
    monthly_labels = []
    monthly_revenue = []
    monthly_sales = []

    for i in range(5, -1, -1):
        m_start = (now - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0)
        m_next = (m_start + timedelta(days=32)).replace(day=1)
        month_label = m_start.strftime('%b %Y')
        monthly_labels.append(month_label)

        m_bookings = bookings_qs.filter(booked_at__gte=m_start, booked_at__lt=m_next)
        rev = m_bookings.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        monthly_revenue.append(float(rev))
        monthly_sales.append(sum(b.total_tickets for b in m_bookings))

    # 2. Sales by Category
    category_data = (
        bookings_qs
        .values('event__category__name')
        .annotate(total_sold=Count('id'), total_rev=Sum('total_amount'))
        .order_by('-total_rev')[:6]
    )
    cat_labels = [c['event__category__name'] or 'General' for c in category_data]
    cat_values = [float(c['total_rev'] or 0) for c in category_data]

    # Fallback chart data if new database
    if not cat_labels:
        cat_labels = ['Tech & AI', 'Music', 'Business', 'Workshops']
        cat_values = [4500, 2800, 1900, 950]

    # 3. Format Breakdown (In-person vs Online vs Hybrid)
    format_counts = {
        'In-Person': events_qs.filter(format='in_person').count(),
        'Online / Virtual': events_qs.filter(format='online').count(),
        'Hybrid': events_qs.filter(format='hybrid').count(),
    }

    # Top selling events
    top_events = (
        events_qs
        .annotate(total_bookings_count=Count('bookings', filter=Q(bookings__status='confirmed')))
        .order_by('-total_bookings_count')[:5]
    )

    context = {
        'total_revenue': total_revenue,
        'total_tickets': total_tickets,
        'total_events_count': total_events_count,
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_revenue_json': json.dumps(monthly_revenue),
        'monthly_sales_json': json.dumps(monthly_sales),
        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),
        'format_labels_json': json.dumps(list(format_counts.keys())),
        'format_values_json': json.dumps(list(format_counts.values())),
        'top_events': top_events,
    }
    return render(request, 'dashboard/reports_analytics.html', context)


@login_required
def export_sales_csv(request):
    """Export complete sales report to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Booking Ref', 'Event Title', 'Attendee', 'Email', 'Amount', 'Payment Status', 'Booked At'])

    if request.user.is_staff:
        bookings = Booking.objects.all().select_related('event')
    else:
        bookings = Booking.objects.filter(event__organizer=request.user).select_related('event')

    for b in bookings:
        writer.writerow([
            b.booking_reference,
            b.event.title,
            b.attendee_name,
            b.attendee_email,
            b.total_amount,
            b.payment_status,
            b.booked_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response


# ==========================================
# 7. NOTIFICATIONS
# ==========================================

@login_required
def notifications_view(request):
    """Notifications Page with filtering and mark as read"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)

    context = {
        'notifications': notifications,
        'filter_type': filter_type,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def mark_all_notifications_read(request):
    """Mark all unread notifications for current user as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications_list')


@login_required
def mark_single_notification_read(request, notif_id):
    """Mark a specific notification as read and redirect to link"""
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications_list')


# ==========================================
# 8. AUTHENTICATION (Login, Register, Logout)
# ==========================================

def register_view(request):
    """User Registration with Attendee or Organizer Role Choice"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            role = form.cleaned_data.get('role', 'attendee')
            phone = form.cleaned_data.get('phone', '')
            org_name = form.cleaned_data.get('organization_name', '')

            UserProfile.objects.create(
                user=user,
                role=role,
                phone=phone,
                organization_name=org_name
            )

            # Welcome notification
            Notification.objects.create(
                user=user,
                title='Welcome to EventPulse!',
                message='Explore thousands of incredible events, book tickets, and connect with vibrant communities.',
                notification_type='system',
                link='/search/'
            )

            login(request, user)
            messages.success(request, f'Welcome to EventPulse, {user.first_name or user.username}!')

            if role == 'organizer':
                return redirect('organizer_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Please fix the errors below to register.')
    else:
        role_param = request.GET.get('role', 'attendee')
        form = UserRegistrationForm(initial={'role': role_param})

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """User Login with Quick-Fill Demo Account Support"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            # Role-based redirection
            if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'admin'):
                return redirect('admin_dashboard')
            elif hasattr(user, 'profile') and user.profile.role == 'organizer':
                return redirect('organizer_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password. Try our quick-fill demo buttons!')

    return render(request, 'auth/login.html')


def logout_view(request):
    """User Logout"""
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('home')

import os
import django
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_platform.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from events.models import (
    UserProfile, Category, Event, TicketTier,
    Booking, TicketItem, Notification, SavedEvent
)

def populate():
    print("=== Populating Sample Database for EventPulse Platform ===")

    # 1. Categories
    categories_data = [
        {
            'name': 'Tech & Artificial Intelligence',
            'icon': 'bi-cpu-fill',
            'description': 'Conferences, hackathons, AI workshops and software developer meetups.'
        },
        {
            'name': 'Music & Concerts',
            'icon': 'bi-music-note-beamed',
            'description': 'Live stadium concerts, electronic music festivals, and intimate acoustic sets.'
        },
        {
            'name': 'Business & Startups',
            'icon': 'bi-briefcase-fill',
            'description': 'Venture capital summits, founder pitch nights, and leadership forums.'
        },
        {
            'name': 'Arts & Culture',
            'icon': 'bi-palette-fill',
            'description': 'Contemporary art galleries, theater performances, and design exhibitions.'
        },
        {
            'name': 'Sports & Fitness',
            'icon': 'bi-trophy-fill',
            'description': 'Marathons, CrossFit championships, yoga retreats, and athletic matches.'
        },
        {
            'name': 'Workshops & Education',
            'icon': 'bi-mortarboard-fill',
            'description': 'Hands-on bootcamps, masterclasses, and executive skill workshops.'
        },
        {
            'name': 'Food & Culinary',
            'icon': 'bi-cup-hot-fill',
            'description': 'Gourmet street food festivals, wine tastings, and chef masterclasses.'
        },
        {
            'name': 'Health & Wellness',
            'icon': 'bi-heart-pulse-fill',
            'description': 'Mindfulness seminars, holistic wellness expos, and mental health symposiums.'
        },
    ]

    cats = {}
    for c_data in categories_data:
        cat, _ = Category.objects.get_or_create(
            name=c_data['name'],
            defaults={'icon': c_data['icon'], 'description': c_data['description']}
        )
        cats[c_data['name']] = cat
    print(f"Created/Verified {len(cats)} Categories.")

    # 2. Demo Users & Profiles
    # Admin
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@eventpulse.com', 'first_name': 'Platform', 'last_name': 'Administrator', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('admin123')
    admin_user.save()
    UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'role': 'admin', 'organization_name': 'EventPulse HQ', 'phone': '+1 (555) 100-2000'}
    )

    # Organizer 1: Sarah Connor (Tech Organizer)
    org1, _ = User.objects.get_or_create(
        username='sarah_connor',
        defaults={'email': 'sarah@summittech.io', 'first_name': 'Sarah', 'last_name': 'Connor'}
    )
    org1.set_password('organizer123')
    org1.save()
    UserProfile.objects.get_or_create(
        user=org1,
        defaults={'role': 'organizer', 'organization_name': 'Summit Tech Media', 'phone': '+1 (415) 890-1234', 'bio': 'Organizing global tech summits, developer bootcamps, and AI summits for 10+ years.'}
    )

    # Organizer 2: Marcus Vance (Music Festivals)
    org2, _ = User.objects.get_or_create(
        username='marcus_vance',
        defaults={'email': 'marcus@soundwavefest.com', 'first_name': 'Marcus', 'last_name': 'Vance'}
    )
    org2.set_password('organizer123')
    org2.save()
    UserProfile.objects.get_or_create(
        user=org2,
        defaults={'role': 'organizer', 'organization_name': 'SoundWave Productions', 'phone': '+1 (310) 555-7890', 'bio': 'Curating unforgettable live music experiences and outdoor festivals worldwide.'}
    )

    # Attendee: Alex Rivera
    attendee, _ = User.objects.get_or_create(
        username='alex_attendee',
        defaults={'email': 'alex.rivera@example.com', 'first_name': 'Alex', 'last_name': 'Rivera'}
    )
    attendee.set_password('attendee123')
    attendee.save()
    UserProfile.objects.get_or_create(
        user=attendee,
        defaults={'role': 'attendee', 'phone': '+1 (650) 333-4455', 'bio': 'Tech enthusiast, live music fan, and frequent workshop attendee.'}
    )
    print("Demo accounts configured (admin, sarah_connor, marcus_vance, alex_attendee).")

    # 3. Events Data
    now = timezone.now()

    sample_events = [
        {
            'title': 'Global AI & Autonomous Agents Summit 2026',
            'organizer': org1,
            'category': cats['Tech & Artificial Intelligence'],
            'short_description': 'Join 3,000+ AI researchers, founders, and engineers exploring next-generation neural reasoning, agent swarms, and robotics.',
            'description': """Welcome to the flagship Artificial Intelligence conference of 2026. Over three immersive days in San Francisco, discover breakthrough architectures, foundation models, multi-agent workflows, and real-world industrial deployments.

Key highlights include:
- Deep dives into agentic workflows and tool-calling systems
- Live technical demonstrations and benchmarks
- Enterprise compliance, ethical guardrails, and security
- Exclusive founder-investor speed networking lounge

Whether you are building new applications or deploying models at scale, this summit connects you with the pioneering minds shaping tomorrow.""",
            'banner_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80',
            'format': 'in_person',
            'venue_name': 'Moscone Convention Center',
            'address': '747 Howard St',
            'city': 'San Francisco, CA',
            'online_meeting_url': '',
            'start_date': now + timedelta(days=5, hours=9),
            'end_date': now + timedelta(days=7, hours=18),
            'status': 'published',
            'is_featured': True,
            'tags': 'AI, Machine Learning, Agents, Python, Deep Learning, Cloud',
            'agenda': """09:00 AM | Keynote: The Dawn of Multi-Agent Systems | Opening address by Chief AI Scientists
11:00 AM | Technical Panel: Reasoning at Scale | Panel with frontier lab researchers
02:00 PM | Hands-on Workshop: Building Autonomous Swarms | Interactive coding lab
05:00 PM | VIP Networking Reception & Demo Showcase | Hors d'oeuvres & drinks""",
            'speakers': """Dr. Elena Vance | VP of AI Research at DeepMind\nAlexandros Thorne | Founder & CEO, HyperScale\nMaya Lin | Head of Autonomous Systems, CloudCorp""",
            'faqs': """Q: Are meals included with tickets?\nA: Yes, continental breakfast, lunch, and evening refreshments are included with all pass tiers.\n\nQ: Is there an online livestream available?\nA: Yes, all keynote stages will be broadcast live for virtual ticket holders.""",
            'tiers': [
                {'name': 'General Delegate Pass', 'price': Decimal('199.00'), 'capacity': 500, 'sold': 120, 'perks': 'Access to all stages, Lunch included, Expo pass'},
                {'name': 'VIP All-Access Pass', 'price': Decimal('499.00'), 'capacity': 100, 'sold': 45, 'perks': 'VIP Lounge access, Speaker dinner invite, Priority seating, Recorded sessions'},
                {'name': 'Student / Academic Entry', 'price': Decimal('49.00'), 'capacity': 150, 'sold': 85, 'perks': 'Stage access with valid student ID'}
            ]
        },
        {
            'title': 'Neon Horizon Electronic Music & Arts Festival',
            'organizer': org2,
            'category': cats['Music & Concerts'],
            'short_description': 'A two-day audiovisual spectacle featuring 4 stages, world-class EDM headliners, holographic laser shows, and immersive installations.',
            'description': """Escape into the rhythm at Neon Horizon 2026. Set across 50 lush acres under the stars, experience world-renowned DJs, cutting-edge spatial audio systems, vibrant visual art installations, and organic culinary villages.

Feel the bass reverberate through high-fidelity sound systems and dance among thousands of music lovers united in celebration of art and sound.""",
            'banner_url': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=1200&auto=format&fit=crop&q=80',
            'format': 'in_person',
            'venue_name': 'Silverstone Amphitheatre Grounds',
            'address': '1200 Festival Way',
            'city': 'Austin, TX',
            'online_meeting_url': '',
            'start_date': now + timedelta(days=12, hours=16),
            'end_date': now + timedelta(days=14, hours=2),
            'status': 'published',
            'is_featured': True,
            'tags': 'EDM, Music Festival, Concert, Live Art, Austin',
            'agenda': """04:00 PM | Gates Open & Sunset Stage Activation | Opening ambient sets
07:00 PM | Mainstage Headliner: Nova Pulse | 2-hour high energy live set
10:30 PM | Holographic Laser Spectacular | Synchronized laser symphony
12:00 AM | After-Hours Neon Tent | Deep house & techno sets""",
            'speakers': """DJ Nova Pulse | International EDM Producer\nKassandra Sky | Live Synth & Vocalist\nEcho & Flux | Ambient Visual Artists""",
            'faqs': """Q: Is there an age restriction?\nA: This event is 18+ only. Government ID will be verified upon wristband collection.\n\nQ: Are lockers available?\nA: Yes, secure lockers with phone charging ports can be rented on site.""",
            'tiers': [
                {'name': 'Weekend General Admission', 'price': Decimal('149.00'), 'capacity': 1200, 'sold': 410, 'perks': '2-Day pass, Access to all 4 stages, Free water stations'},
                {'name': 'VIP Backstage Experience', 'price': Decimal('349.00'), 'capacity': 200, 'sold': 88, 'perks': 'Backstage viewing deck, Private restrooms, Express entry, 3 drink vouchers'}
            ]
        },
        {
            'title': 'Silicon Valley Founder & Angel Pitch Summit 2026',
            'organizer': org1,
            'category': cats['Business & Startups'],
            'short_description': 'Where 50 vetted seed and Series-A startups pitch directly to 120+ top-tier angels, venture capitalists, and family offices.',
            'description': """Pitch, partner, and scale. The Silicon Valley Founder & Angel Pitch Summit brings together high-growth tech entrepreneurs and accredited venture investors for high-impact pitch rounds, 1-on-1 deal rooms, and masterclasses on fundraising strategy.""",
            'banner_url': 'https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=1200&auto=format&fit=crop&q=80',
            'format': 'hybrid',
            'venue_name': 'Stanford Park Conference Center & Zoom',
            'address': '100 El Camino Real',
            'city': 'Palo Alto, CA',
            'online_meeting_url': 'https://zoom.us/j/9876543210',
            'start_date': now + timedelta(days=8, hours=8, minutes=30),
            'end_date': now + timedelta(days=8, hours=17, minutes=30),
            'status': 'published',
            'is_featured': True,
            'tags': 'Startups, Venture Capital, Pitch, Angel Investors, Silicon Valley',
            'agenda': """08:30 AM | Breakfast & Investor Registration | Networking lounge open
09:30 AM | FinTech & AI Startup Pitch Track | 15 curated company pitches
01:30 PM | Keynote: Navigating SaaS Valuations | Senior Partner at Sequoia
03:30 PM | 1-on-1 Deal Rooms & Term Sheet Discussions | Private meetings""",
            'speakers': """David Chen | Managing Partner, Horizon Ventures\nSophia Patel | GP at Matrix Capital\nMarcus Brody | 3x Exited Founder & Angel""",
            'faqs': """Q: Can founders pitch virtually?\nA: Yes! Virtual pitch slots are fully supported via our dedicated interactive video stage.""",
            'tiers': [
                {'name': 'Founder In-Person Pass', 'price': Decimal('99.00'), 'capacity': 150, 'sold': 95, 'perks': 'Pitch consideration, Full day access, Lunch & Coffee'},
                {'name': 'Virtual Livestream & Pitch Deck Access', 'price': Decimal('0.00'), 'capacity': 1000, 'sold': 340, 'perks': 'Full HD livestream, Digital pitch deck compendium'},
                {'name': 'Accredited Investor Pass', 'price': Decimal('249.00'), 'capacity': 100, 'sold': 62, 'perks': 'Access to private Deal Room, Startup founder contact list'}
            ]
        },
        {
            'title': 'Masterclass: Modern Full-Stack Python & Django Microservices',
            'organizer': org1,
            'category': cats['Workshops & Education'],
            'short_description': 'An intensive, hands-on masterclass architecting high-throughput Django web applications with asynchronous tasks, Redis, and Bootstrap 5.',
            'description': """Level up your backend and full-stack software development skills. In this intensive full-day masterclass, you will build and deploy a production-ready application architecture using Python Django, PostgreSQL, Celery, and modern frontend styling.""",
            'banner_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&auto=format&fit=crop&q=80',
            'format': 'online',
            'venue_name': 'Online Interactive Webinar',
            'address': 'Zoom Platform',
            'city': 'Global Virtual',
            'online_meeting_url': 'https://zoom.us/j/1234567890',
            'start_date': now + timedelta(days=3, hours=10),
            'end_date': now + timedelta(days=3, hours=16),
            'status': 'published',
            'is_featured': False,
            'tags': 'Python, Django, Web Development, Full Stack, Coding',
            'agenda': """10:00 AM | Module 1: Django Architectural Deep Dive | Models, caching & DB optimization
12:00 PM | Module 2: High Performance APIs & Auth | JWT, sessions & security
02:00 PM | Module 3: Frontend Mastery with Bootstrap 5 | Modern UI components & JS
04:00 PM | Module 4: Deployment & Live Code Review | Production checklist & Q&A""",
            'speakers': """Sarah Connor | Principal Software Architect\nDr. Jordan Bell | Python Core Contributor""",
            'faqs': """Q: Will the workshop be recorded?\nA: Yes, all attendees receive permanent access to the 4K recording and GitHub repository.""",
            'tiers': [
                {'name': 'Free Community Ticket', 'price': Decimal('0.00'), 'capacity': 300, 'sold': 180, 'perks': 'Live webinar access, Chat participation'},
                {'name': 'Pro Ticket + Course Code & Certificate', 'price': Decimal('39.00'), 'capacity': 100, 'sold': 58, 'perks': 'Permanent recordings, GitHub starter repo, Verified certificate'}
            ]
        },
        {
            'title': 'Luminescence: Contemporary Art & Interactive Light Gallery',
            'organizer': org2,
            'category': cats['Arts & Culture'],
            'short_description': 'Walk through glowing rooms of interactive optical illusions, generative art canvases, and kinetic light sculptures.',
            'description': """An ethereal sensory journey where technology meets human emotion. Luminescence features over 20 monumental light sculptures by international visual artists, reactive mirror rooms, and ambient spatial soundscapes.""",
            'banner_url': 'https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1200&auto=format&fit=crop&q=80',
            'format': 'in_person',
            'venue_name': 'Metropolitan Arts Pavilion',
            'address': '450 West 14th Street',
            'city': 'New York, NY',
            'online_meeting_url': '',
            'start_date': now + timedelta(days=6, hours=11),
            'end_date': now + timedelta(days=6, hours=21),
            'status': 'published',
            'is_featured': False,
            'tags': 'Art Exhibition, Light Art, New York, Culture, Gallery',
            'agenda': """11:00 AM | Gallery Doors Open | Timed hourly entries
03:00 PM | Curators Tour & Artist Talk | Inside the creation process
07:00 PM | Twilight Glow Sessions | Cocktail lounge & live jazz trio""",
            'speakers': """Julian Moreau | French Kinetic Sculptor\nNaomi Takahashi | Generative AI Artist""",
            'faqs': """Q: Is photography allowed?\nA: Photography is warmly welcomed! Tripods and flash are prohibited.""",
            'tiers': [
                {'name': 'Standard Entry Pass', 'price': Decimal('28.00'), 'capacity': 400, 'sold': 210, 'perks': 'Full gallery entry for 90 minutes'},
                {'name': 'VIP Cocktail & Evening Pass', 'price': Decimal('65.00'), 'capacity': 80, 'sold': 42, 'perks': 'Complimentary craft cocktail, Priority entry, Exhibition catalog'}
            ]
        },
        {
            'title': 'Metro Marathon & 10K Fitness Championship 2026',
            'organizer': org2,
            'category': cats['Sports & Fitness'],
            'short_description': 'Run along scenic waterfront routes with 8,000 athletes, cheering crowds, live timing chips, and celebratory finish festival.',
            'description': """Whether you are setting a personal record or jogging with friends, the Metro Marathon is the premier running celebration of the season. Includes official finisher medals, dri-fit technical shirts, and electrolyte recovery stations.""",
            'banner_url': 'https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=1200&auto=format&fit=crop&q=80',
            'format': 'in_person',
            'venue_name': 'Lakefront Athletic Park',
            'address': '1000 Waterfront Blvd',
            'city': 'Chicago, IL',
            'online_meeting_url': '',
            'start_date': now + timedelta(days=16, hours=7),
            'end_date': now + timedelta(days=16, hours=14),
            'status': 'published',
            'is_featured': False,
            'tags': 'Marathon, 10K, Fitness, Running, Chicago',
            'agenda': """07:00 AM | Full Marathon Wave 1 Start | Elite runners
07:45 AM | 10K Run Wave 2 Start | Open participants
11:00 AM | Awards Ceremony & Live Band | Medals presentation
12:30 PM | Recovery Village & Food Trucks | Stretching & celebration""",
            'speakers': """Coach Ryan Miller | Olympic Marathoner\nDr. Sarah Adams | Sports Nutritionist""",
            'faqs': """Q: Where do I collect my runner bib?\nA: Bib pickup is open Thursday and Friday before race day at the Expo center.""",
            'tiers': [
                {'name': '10K Race Entry', 'price': Decimal('45.00'), 'capacity': 2000, 'sold': 850, 'perks': 'Timing chip, Finisher medal, Official t-shirt'},
                {'name': 'Full Marathon (42.2km) Entry', 'price': Decimal('85.00'), 'capacity': 1500, 'sold': 720, 'perks': 'Marathon medal, Tech jacket, Recovery pack'}
            ]
        },
        {
            'title': 'Global Street Food & Craft Beer Fiesta',
            'organizer': org2,
            'category': cats['Food & Culinary'],
            'short_description': 'Taste authentic cuisines from 35 international street vendors, sample 50+ craft brews, and enjoy live acoustic performances.',
            'description': """An epicurean paradise celebrating worldwide culinary traditions. Savor authentic wood-fired pizzas, smoky Texas barbecue, delicate Tokyo ramen, aromatic Oaxacan tacos, and award-winning microbrews from regional brewmasters.""",
            'banner_url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200&auto=format&fit=crop&q=80',
            'format': 'in_person',
            'venue_name': 'Pier 42 Waterfront Promenade',
            'address': 'Pier 42 Maritime Blvd',
            'city': 'Seattle, WA',
            'online_meeting_url': '',
            'start_date': now + timedelta(days=9, hours=12),
            'end_date': now + timedelta(days=10, hours=20),
            'status': 'published',
            'is_featured': True,
            'tags': 'Food, Beer, Street Food, Seattle, Tasting, Culinary',
            'agenda': """12:00 PM | Fiesta Gates Open & Food Stalls Live\n02:00 PM | Artisan Craft Beer Masterclass\n05:00 PM | Chili Pepper Eating Challenge\n07:00 PM | Sunset Acoustic Concert""",
            'speakers': """Chef Marco Santoro | Michelin Bib Gourmand Chef\nClara Higgins | Master Cicerone""",
            'faqs': """Q: Are vegetarian and vegan options available?\nA: Absolutely! Over 40% of vendors offer curated plant-based items.""",
            'tiers': [
                {'name': 'General Admission Entry', 'price': Decimal('15.00'), 'capacity': 3000, 'sold': 1200, 'perks': 'Entry wristband, Souvenir tasting cup'},
                {'name': 'Craft Beer Tasting Pass (10 Pours)', 'price': Decimal('45.00'), 'capacity': 800, 'sold': 490, 'perks': '10 craft beer tasting tokens, Express lines, Souvenir glass'}
            ]
        },
        {
            'title': 'Mindful Living & Holistic Wellness Weekend Retreat',
            'organizer': org1,
            'category': cats['Health & Wellness'],
            'short_description': 'Reconnect with your inner calm through guided meditation, breathwork workshops, sunrise yoga, and sound bath therapy.',
            'description': """Step away from the noise of the digital world. Guided by certified mindfulness facilitators and holistic health practitioners, nurture your mental clarity and physical vitality in a tranquil sanctuary.""",
            'banner_url': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1200&auto=format&fit=crop&q=80',
            'format': 'in_person',
            'venue_name': 'Serenity Valley Botanical Gardens',
            'address': '880 Pine Ridge Trail',
            'city': 'Boulder, CO',
            'online_meeting_url': '',
            'start_date': now + timedelta(days=20, hours=8),
            'end_date': now + timedelta(days=21, hours=17),
            'status': 'published',
            'is_featured': False,
            'tags': 'Yoga, Meditation, Wellness, Sound Bath, Boulder',
            'agenda': """08:00 AM | Sunrise Vinyasa Flow on the Lawn\n10:30 AM | Science of Breathwork & Nervous System Reset\n01:00 PM | Organic Farm-to-Table Lunch\n03:30 PM | Crystal Singing Bowl Sound Immersion""",
            'speakers': """Aria Sol | Sound Therapist & Yoga Master\nDr. Marcus Hayes | Neurobiologist & Author""",
            'faqs': """Q: What should I bring?\nA: Bring comfortable clothing and a water bottle. High quality mats and props are provided.""",
            'tiers': [
                {'name': 'Single Day Pass (Saturday)', 'price': Decimal('79.00'), 'capacity': 100, 'sold': 48, 'perks': 'Full day workshops, Organic lunch included'},
                {'name': 'Full Weekend Immersion Pass', 'price': Decimal('139.00'), 'capacity': 60, 'sold': 35, 'perks': '2 days access, Gift bag, Evening sound bath pass'}
            ]
        }
    ]

    created_events = []
    for ev_data in sample_events:
        tiers_info = ev_data.pop('tiers')
        event, created = Event.objects.get_or_create(
            title=ev_data['title'],
            defaults=ev_data
        )
        created_events.append(event)

        # Create tiers
        for t_info in tiers_info:
            TicketTier.objects.get_or_create(
                event=event,
                name=t_info['name'],
                defaults={
                    'price': t_info['price'],
                    'capacity': t_info['capacity'],
                    'tickets_sold': t_info['sold'],
                    'perks': t_info['perks'],
                    'is_active': True
                }
            )

    print(f"Created {len(created_events)} rich events with ticket tiers.")

    # 4. Sample Bookings for Alex Rivera (Attendee)
    first_event = created_events[0]
    tier_vip = first_event.ticket_tiers.filter(name__icontains='VIP').first() or first_event.ticket_tiers.first()
    
    booking1, _ = Booking.objects.get_or_create(
        user=attendee,
        event=first_event,
        defaults={
            'total_amount': tier_vip.price + Decimal('14.97'),
            'status': 'confirmed',
            'payment_status': 'paid',
            'payment_method': 'Credit Card (Visa •••• 4242)',
            'attendee_name': 'Alex Rivera',
            'attendee_email': 'alex.rivera@example.com',
            'attendee_phone': '+1 (650) 333-4455',
            'notes': 'Looking forward to the agent swarms session!'
        }
    )
    TicketItem.objects.get_or_create(
        booking=booking1,
        ticket_tier=tier_vip,
        defaults={
            'quantity': 1,
            'unit_price': tier_vip.price,
            'subtotal': tier_vip.price,
        }
    )

    # Booking 2: Silicon Valley Pitch Summit (Free ticket)
    third_event = created_events[2]
    free_tier = third_event.ticket_tiers.filter(price=0).first() or third_event.ticket_tiers.first()
    booking2, _ = Booking.objects.get_or_create(
        user=attendee,
        event=third_event,
        defaults={
            'total_amount': Decimal('0.00'),
            'status': 'confirmed',
            'payment_status': 'free',
            'payment_method': 'Free Pass',
            'attendee_name': 'Alex Rivera',
            'attendee_email': 'alex.rivera@example.com',
            'attendee_phone': '+1 (650) 333-4455',
        }
    )
    TicketItem.objects.get_or_create(
        booking=booking2,
        ticket_tier=free_tier,
        defaults={
            'quantity': 1,
            'unit_price': Decimal('0.00'),
            'subtotal': Decimal('0.00'),
        }
    )

    # Booking 3 for Sarah Connor's event (organizer sales feed)
    booking3, _ = Booking.objects.get_or_create(
        user=admin_user,
        event=first_event,
        defaults={
            'total_amount': Decimal('199.00'),
            'status': 'confirmed',
            'payment_status': 'paid',
            'payment_method': 'Mastercard •••• 8812',
            'attendee_name': 'Dr. Samantha Hayes',
            'attendee_email': 'samantha.hayes@caltech.edu',
            'attendee_phone': '+1 (626) 555-0199',
            'notes': 'Faculty attendee.'
        }
    )
    gen_tier = first_event.ticket_tiers.filter(price__gt=0).first()
    if gen_tier:
        TicketItem.objects.get_or_create(
            booking=booking3,
            ticket_tier=gen_tier,
            defaults={'quantity': 1, 'unit_price': gen_tier.price, 'subtotal': gen_tier.price}
        )

    # 5. Saved Events for Alex Rivera
    SavedEvent.objects.get_or_create(user=attendee, event=created_events[1]) # Neon Horizon
    SavedEvent.objects.get_or_create(user=attendee, event=created_events[3]) # Python Masterclass

    # 6. Sample Notifications
    notifications_data = [
        {
            'user': attendee,
            'title': 'Booking Confirmed!',
            'message': f'Your pass for "{first_event.title}" is confirmed. Booking ref: {booking1.booking_reference}',
            'notification_type': 'booking_confirmed',
            'link': f'/booking/{booking1.booking_reference}/',
            'is_read': False
        },
        {
            'user': attendee,
            'title': 'Free Registration Confirmed',
            'message': f'You are registered for "{third_event.title}". Check your e-ticket pass.',
            'notification_type': 'booking_confirmed',
            'link': f'/booking/{booking2.booking_reference}/',
            'is_read': True
        },
        {
            'user': org1,
            'title': 'New Ticket Sold!',
            'message': f'Alex Rivera just registered for "{first_event.title}" (${booking1.total_amount}).',
            'notification_type': 'ticket_sold',
            'link': '/dashboard/organizer/',
            'is_read': False
        },
        {
            'user': org1,
            'title': 'Event Reached 150 Attendees!',
            'message': f'"{first_event.title}" has crossed 150 ticket registrations. Great momentum!',
            'notification_type': 'system',
            'link': '/dashboard/organizer/',
            'is_read': False
        },
    ]

    for n in notifications_data:
        Notification.objects.get_or_create(
            user=n['user'],
            title=n['title'],
            defaults=n
        )

    print("Sample database successfully seeded with events, tickets, bookings, and notifications!")

if __name__ == '__main__':
    populate()

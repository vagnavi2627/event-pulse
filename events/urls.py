from django.urls import path
from . import views

urlpatterns = [
    # Organizer Event CRUD (Must come before dynamic slug)
    path('event/new/', views.create_event_view, name='create_event'),
    path('event/<int:event_id>/edit/', views.edit_event_view, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event_view, name='delete_event'),
    path('event/<int:event_id>/attendees/', views.event_attendees_view, name='event_attendees'),
    path('event/<int:event_id>/attendees/export/', views.export_attendees_csv, name='export_attendees_csv'),

    # Public & Discovery
    path('', views.home_view, name='home'),
    path('search/', views.search_events_view, name='search_events'),
    path('event/<slug:slug>/', views.event_detail_view, name='event_detail'),
    
    # Booking & Tickets
    path('event/<slug:slug>/book/', views.book_ticket_view, name='book_ticket'),
    path('booking/<str:booking_ref>/', views.ticket_detail_view, name='ticket_detail'),
    path('booking/<str:booking_ref>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    
    # User / Attendee Dashboard
    path('dashboard/user/', views.user_dashboard_view, name='user_dashboard'),
    path('events/<int:event_id>/bookmark/', views.toggle_bookmark_view, name='toggle_bookmark'),

    # Organizer Dashboard
    path('dashboard/organizer/', views.organizer_dashboard_view, name='organizer_dashboard'),

    # Admin Dashboard
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/admin/event/<int:event_id>/toggle/', views.admin_toggle_event_status, name='admin_toggle_event_status'),
    path('dashboard/admin/user/<int:user_id>/role/', views.admin_toggle_user_role, name='admin_toggle_user_role'),

    # Reports & Analytics
    path('dashboard/analytics/', views.reports_analytics_view, name='reports_analytics'),
    path('dashboard/sales/export/', views.export_sales_csv, name='export_sales_csv'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications_list'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notif_id>/read/', views.mark_single_notification_read, name='mark_single_notification_read'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

from .models import Category, Notification, UserProfile

def global_context(request):
    context = {
        'global_categories': Category.objects.all(),
        'unread_notifications_count': 0,
        'recent_notifications': [],
        'user_profile': None,
    }

    if request.user.is_authenticated:
        try:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            context['user_profile'] = profile
        except Exception:
            context['user_profile'] = None

        user_notifications = Notification.objects.filter(user=request.user)
        context['unread_notifications_count'] = user_notifications.filter(is_read=False).count()
        context['recent_notifications'] = user_notifications[:5]

    return context

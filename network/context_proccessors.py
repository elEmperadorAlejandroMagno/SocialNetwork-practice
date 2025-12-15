from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(receiver=request.user, is_read=False).select_related('sender', 'post')
        return { 'notifications': user_notifications }
    return { 'notifications': [] }
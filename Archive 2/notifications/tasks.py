from celery import shared_task
from django.utils import timezone
from .models import Notification

@shared_task
def cleanup_expired_notifications():
    Notification.objects.filter(expires_at__lte=timezone.now()).delete()
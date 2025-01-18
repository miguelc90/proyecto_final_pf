from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserSession
from django.utils import timezone

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    UserSession.objects.create(user=user, login_time=timezone.now())

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    session = UserSession.objects.filter(user=user).last()
    if session:
        session.logout_time = timezone.now()
        session.save()

# signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserInfo, SellerInfo

@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        UserInfo.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def create_seller_info(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        SellerInfo.objects.get_or_create(user=instance)

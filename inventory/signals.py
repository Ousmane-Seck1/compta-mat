from __future__ import annotations

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import UserProfile, Voucher


User = get_user_model()
CENTRAL_RECAP_CACHE_VERSION_KEY = "central_recap:version"


def _invalidate_central_recap_cache() -> None:
    version = cache.get(CENTRAL_RECAP_CACHE_VERSION_KEY)
    if version is None:
        version = 1
    cache.set(CENTRAL_RECAP_CACHE_VERSION_KEY, int(version) + 1, timeout=None)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Voucher)
def invalidate_central_cache_on_voucher_save(sender, instance, **kwargs):
    _invalidate_central_recap_cache()


@receiver(post_delete, sender=Voucher)
def invalidate_central_cache_on_voucher_delete(sender, instance, **kwargs):
    _invalidate_central_recap_cache()

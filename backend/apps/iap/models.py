from django.db import models
from django.conf import settings
from django.utils import timezone


class InAppPurchase(models.Model):
    class Platform(models.TextChoices):
        IOS = 'ios', 'iOS'
        ANDROID = 'android', 'Android'

    class PurchaseType(models.TextChoices):
        SUBSCRIPTION = 'subscription', 'Subscription'
        LIFETIME = 'lifetime', 'Lifetime'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='iap_purchases'
    )
    platform = models.CharField(max_length=10, choices=Platform.choices)
    product_id = models.CharField(max_length=255)
    purchase_type = models.CharField(max_length=12, choices=PurchaseType.choices)
    original_transaction_id = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255, blank=True)
    purchase_date = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    purchase_token = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    raw_store_resp = models.JSONField(null=True, blank=True)
    environment = models.CharField(max_length=20, default='Production')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'iap_purchases'
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['user', 'is_verified', 'expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.product_id} — {'active' if self.is_active else 'inactive'}"

    @property
    def is_expired(self):
        if self.purchase_type == self.PurchaseType.LIFETIME:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def deactivate_if_expired(self):
        if self.is_expired and self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active'])
            return True
        return False

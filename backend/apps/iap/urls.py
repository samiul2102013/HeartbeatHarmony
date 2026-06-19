from django.urls import path
from . import views

urlpatterns = [
    path('purchases/verify', views.VerifyPurchaseView.as_view(), name='iap-verify'),
    path('users/me/premium', views.PremiumStatusView.as_view(), name='iap-premium-status'),
    path('webhooks/google-play', views.GooglePlayWebhookView.as_view(), name='iap-google-webhook'),
]

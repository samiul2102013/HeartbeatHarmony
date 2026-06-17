from django.urls import path
from . import views

urlpatterns = [
    path('api/iap/verify/', views.VerifyReceiptView.as_view(), name='iap-verify'),
    path('api/iap/restore/', views.RestorePurchasesView.as_view(), name='iap-restore'),
    path('api/user/premium/', views.PremiumStatusView.as_view(), name='user-premium'),
]

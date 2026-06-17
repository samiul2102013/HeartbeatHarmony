from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

from .models import InAppPurchase
from .serializers import (
    VerifyReceiptSerializer,
    RestoreReceiptSerializer,
    PremiumStatusSerializer,
)
from .apple_utils import (
    validate_apple_receipt,
    extract_purchase_info,
    AppleValidationError,
    MONTHLY_PRODUCT_ID,
    LIFETIME_PRODUCT_ID,
)
from apps.core.response_utils import success_response, error_response


def _build_premium_data(user):
    active_purchase = InAppPurchase.objects.filter(
        user=user, is_active=True
    ).order_by('-purchase_date').first()

    if active_purchase and active_purchase.is_expired:
        active_purchase.deactivate_if_expired()
        active_purchase = None

    if not active_purchase:
        return {
            'isPremium': False,
            'productId': None,
            'purchaseType': None,
            'expiresAt': None,
        }

    return {
        'isPremium': True,
        'productId': active_purchase.product_id,
        'purchaseType': active_purchase.purchase_type,
        'expiresAt': active_purchase.expires_at,
    }


def _process_purchases(user, purchases):
    created = []
    for info in purchases:
        obj, was_created = InAppPurchase.objects.update_or_create(
            original_transaction_id=info['original_transaction_id'],
            defaults={
                'user': user,
                'platform': 'ios',
                'product_id': info['product_id'],
                'purchase_type': info['purchase_type'],
                'transaction_id': info['transaction_id'],
                'purchase_date': info['purchase_date'],
                'expires_at': info['expires_at'],
                'is_active': info['is_active'],
                'environment': info['environment'],
            },
        )
        if was_created:
            created.append(obj)

    # Update user's plan
    has_active = InAppPurchase.objects.filter(
        user=user, is_active=True
    ).exclude(is_expired=True).exists()

    if has_active and user.plan != 'pro':
        user.plan = 'pro'
        user.save(update_fields=['plan'])
    elif not has_active and user.plan == 'pro':
        # Don't auto-downgrade here — let a cron/check handle that
        pass

    return created


class VerifyReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = VerifyReceiptSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                'Invalid request',
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        receipt_data = serializer.validated_data['receipt']

        try:
            validation = validate_apple_receipt(receipt_data)
            purchases = extract_purchase_info(validation)
        except AppleValidationError as e:
            return error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not purchases:
            return error_response(
                'No valid purchases found in receipt',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        _process_purchases(request.user, purchases)
        premium = _build_premium_data(request.user)

        return success_response(
            data=premium,
            message='Receipt verified',
        )


class PremiumStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        premium = _build_premium_data(request.user)
        return success_response(data=premium)


class RestorePurchasesView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = RestoreReceiptSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                'Invalid request',
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        receipt_data = serializer.validated_data['receipt']

        try:
            validation = validate_apple_receipt(receipt_data)
            purchases = extract_purchase_info(validation)
        except AppleValidationError as e:
            return error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not purchases:
            return error_response(
                'No valid purchases found in receipt',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        _process_purchases(request.user, purchases)
        premium = _build_premium_data(request.user)

        return success_response(
            data=premium,
            message='Purchases restored',
        )

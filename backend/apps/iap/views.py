import json
import logging
from datetime import timedelta

from django.utils import timezone
from django.db import models as dm

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

logger = logging.getLogger(__name__)

from .models import InAppPurchase
from .serializers import PurchaseVerifySerializer, PremiumStatusSerializer
from .store_clients import (
    verify_android_purchase,
    verify_ios_purchase,
    MONTHLY_PRODUCT_IDS,
    LIFETIME_PRODUCT_IDS,
    MONTHLY_DURATION_DAYS,
)

class VerifyThrottle(UserRateThrottle):
    rate = '10/minute'

class VerifyPurchaseView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [VerifyThrottle]

    def post(self, request):
        logger.info(f'VerifyPurchase request body: {json.dumps(request.data, default=str)}')

        serializer = PurchaseVerifySerializer(data=request.data)
        if not serializer.is_valid():
            resp = Response(
                {'error': 'invalid_payload', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
            logger.warning(f'VerifyPurchase response 400: {json.dumps(resp.data, default=str)}')
            return resp

        data = serializer.validated_data
        platform = data['platform']
        product_id = data['product_id']
        purchase_token = data['purchase_token']
        transaction_id = data['transaction_id']

        if product_id not in MONTHLY_PRODUCT_IDS and product_id not in LIFETIME_PRODUCT_IDS:
            resp = Response(
                {'error': 'invalid_payload', 'details': 'Unknown product_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )
            logger.warning(f'VerifyPurchase unknown product_id: {product_id}')
            return resp

        # Idempotency — same token already stored
        existing = InAppPurchase.objects.filter(purchase_token=purchase_token).first()
        if existing:
            is_active = existing.is_verified and (
                existing.expires_at is None or existing.expires_at > timezone.now()
            )
            resp = Response(
                PremiumStatusSerializer({
                    'is_premium': is_active,
                    'expires_at': existing.expires_at,
                }).data,
                status=status.HTTP_200_OK,
            )
            logger.info(f'VerifyPurchase duplicate token, response 200: {json.dumps(resp.data, default=str)}')
            return resp

        # Verify with the store
        try:
            if platform == 'android':
                verified, raw_resp, expires_at = verify_android_purchase(product_id, purchase_token)
                logger.info(f'Android verify result: verified={verified}, expires_at={expires_at}')
            else:
                verified, raw_resp, expires_at = verify_ios_purchase(purchase_token)
                logger.info(f'iOS verify result: verified={verified}, expires_at={expires_at}')
        except Exception as e:
            logger.error(f'Store API error: {e}', exc_info=True)
            return Response(
                {'error': 'store_api_error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not verified:
            resp = Response(
                {'error': 'purchase_not_verified'},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
            logger.warning(f'VerifyPurchase not verified, response 402')
            return resp

        # Fallback: compute expiry for monthly if store didn't provide one
        expires_at_dt = None
        if expires_at:
            expires_at_dt = timezone.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        elif product_id in MONTHLY_PRODUCT_IDS:
            expires_at_dt = timezone.now() + timedelta(days=MONTHLY_DURATION_DAYS)

        purchase_type = 'lifetime' if product_id in LIFETIME_PRODUCT_IDS else 'subscription'

        InAppPurchase.objects.create(
            user=request.user,
            platform=platform,
            product_id=product_id,
            purchase_type=purchase_type,
            original_transaction_id=transaction_id,
            transaction_id=transaction_id,
            purchase_date=timezone.now(),
            expires_at=expires_at_dt,
            purchase_token=purchase_token,
            is_verified=True,
            is_active=True,
            raw_store_resp=raw_resp,
        )

        # Upgrade user's plan
        if request.user.plan != 'pro':
            try:
                request.user.plan = 'pro'
                request.user.save(update_fields=['plan'])
            except Exception:
                pass

        resp = Response(
            PremiumStatusSerializer({
                'is_premium': True,
                'expires_at': expires_at_dt,
            }).data,
            status=status.HTTP_201_CREATED,
        )
        logger.info(f'VerifyPurchase success, response 201: {json.dumps(resp.data, default=str)}')
        return resp


class PremiumStatusView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [VerifyThrottle]

    def get(self, request):
        purchase = (
            InAppPurchase.objects
            .filter(user=request.user, is_verified=True)
            .filter(dm.Q(expires_at__isnull=True) | dm.Q(expires_at__gt=timezone.now()))
            .order_by('-created_at')
            .first()
        )
        if purchase:
            resp = Response(
                PremiumStatusSerializer({
                    'is_premium': True,
                    'expires_at': purchase.expires_at,
                }).data,
            )
        else:
            resp = Response(
                PremiumStatusSerializer({'is_premium': False, 'expires_at': None}).data,
            )
        logger.info(f'PremiumStatus user={request.user.id} response: {json.dumps(resp.data, default=str)}')
        return resp

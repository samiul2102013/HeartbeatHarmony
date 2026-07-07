import json
import base64
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
    cancel_android_subscription,
    cancel_ios_subscription,
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


class CancelSubscriptionView(APIView):
    """
    POST /purchases/cancel
    Cancels the authenticated user's active monthly subscription at the app store,
    then sets plan=free and deactivates the purchase in the database.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        purchase = (
            InAppPurchase.objects
            .filter(user=request.user, is_verified=True, is_active=True, purchase_type='subscription')
            .order_by('-created_at')
            .first()
        )
        if not purchase:
            return Response({'error': 'No active subscription found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            if purchase.platform == 'android':
                cancel_android_subscription(purchase.purchase_token, purchase.product_id)
            elif purchase.platform == 'ios':
                cancel_ios_subscription(purchase.original_transaction_id)
            else:
                return Response({'error': 'Unknown platform'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            purchase.is_active = False
            purchase.save(update_fields=['is_active'])

            if request.user.plan != 'free':
                request.user.plan = 'free'
                request.user.save(update_fields=['plan'])

            logger.info(f'Subscription cancelled for user={request.user.id}, purchase_id={purchase.id}')
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Cancel subscription failed for user={request.user.id}: {e}', exc_info=True)
            return Response({'error': 'Failed to cancel subscription at store'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GooglePlayWebhookView(APIView):
    """
    POST /webhooks/google-play
    Receives Real-time Developer Notifications from Google Play via Pub/Sub.
    Handles subscription cancellation, expiry, and other lifecycle events.
    No auth — Google signs the request via Pub/Sub verification.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            data = request.data
            message = data.get('message', {})
            encoded = message.get('data', '')
            if not encoded:
                logger.warning('GooglePlay webhook: no data in message')
                return Response(status=status.HTTP_200_OK)

            import base64, json
            decoded = base64.b64decode(encoded).decode('utf-8')
            payload = json.loads(decoded)

            dev_notification = payload.get('developerNotification', {})
            sub_notification = dev_notification.get('subscriptionNotification', {})
            if not sub_notification:
                logger.info('GooglePlay webhook: not a subscription notification')
                return Response(status=status.HTTP_200_OK)

            notification_type = sub_notification.get('notificationType')
            purchase_token = sub_notification.get('purchaseToken')
            product_id = sub_notification.get('subscriptionId')

            logger.info(f'GooglePlay webhook: type={notification_type}, token={purchase_token}, product={product_id}')

            if not purchase_token:
                logger.warning('GooglePlay webhook: no purchaseToken')
                return Response(status=status.HTTP_200_OK)

            purchase = InAppPurchase.objects.filter(purchase_token=purchase_token).first()
            if not purchase:
                logger.warning(f'GooglePlay webhook: purchase not found for token {purchase_token[:20]}...')
                return Response(status=status.HTTP_200_OK)

            # Notification types:
            # 3 = SUBSCRIPTION_CANCELED, 12 = SUBSCRIPTION_REVOKED, 13 = SUBSCRIPTION_EXPIRED
            if notification_type in (3, 12, 13):
                purchase.is_active = False
                purchase.save(update_fields=['is_active'])
                logger.info(f'GooglePlay webhook: deactivated purchase {purchase.id} for user {purchase.user.id}')

                if purchase.user.plan != 'free':
                    purchase.user.plan = 'free'
                    purchase.user.save(update_fields=['plan'])
                    logger.info(f'GooglePlay webhook: set user {purchase.user.id} plan to free')

            # 7 = SUBSCRIPTION_RESTARTED — user resubscribed
            elif notification_type == 7:
                purchase.is_active = True
                purchase.save(update_fields=['is_active'])

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'GooglePlay webhook error: {e}', exc_info=True)
            return Response(status=status.HTTP_200_OK)


class AppleAppStoreWebhookView(APIView):
    """
    POST /webhooks/app-store
    Receives App Store Server Notifications v2 (signed JWS payloads).
    Handles subscription lifecycle events: new subscriptions, renewals,
    failures, cancellations, and refunds.
    """
    authentication_classes = []
    permission_classes = []

    def _decode_jws_payload(self, signed_payload: str) -> dict | None:
        """Decode the payload portion of a JWS without full signature verification."""
        try:
            parts = signed_payload.split('.')
            if len(parts) != 3:
                return None
            payload_b64 = parts[1]
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += '=' * padding
            return json.loads(base64.urlsafe_b64decode(payload_b64))
        except Exception:
            return None

    def _verify_jws(self, signed_payload: str) -> dict | None:
        """Verify the JWS signature using the x5c certificate chain in the header."""
        try:
            parts = signed_payload.split('.')
            if len(parts) != 3:
                return None

            from cryptography import x509
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.backends import default_backend

            header_b64 = parts[0]
            payload_b64 = parts[1]
            signature_b64 = parts[2]

            # Decode header
            pad = 4 - len(header_b64) % 4
            if pad != 4:
                header_b64 += '=' * pad
            header = json.loads(base64.urlsafe_b64decode(header_b64))

            x5c = header.get('x5c', [])
            if not x5c:
                return None

            # Use the leaf certificate to verify
            cert_der = base64.b64decode(x5c[0])
            cert = x509.load_der_x509_certificate(cert_der, default_backend())
            public_key = cert.public_key()

            message = f'{parts[0]}.{parts[1]}'.encode('utf-8')
            pad = 4 - len(signature_b64) % 4
            if pad != 4:
                signature_b64 += '=' * pad
            signature = base64.urlsafe_b64decode(signature_b64)

            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))

            return json.loads(base64.urlsafe_b64decode(payload_b64 + '=='))
        except Exception as e:
            logger.error(f'Apple JWS verification failed: {e}', exc_info=True)
            return None

    def post(self, request):
        try:
            signed_payload = request.data.get('signedPayload', '')
            if not signed_payload:
                logger.warning('Apple webhook: no signedPayload')
                return Response(status=status.HTTP_200_OK)

            notification = self._verify_jws(signed_payload)
            if not notification:
                notification = self._decode_jws_payload(signed_payload)
                if not notification:
                    logger.warning('Apple webhook: failed to decode JWS payload')
                    return Response(status=status.HTTP_200_OK)

            notification_type = notification.get('notificationType', '')
            subtype = notification.get('subtype', '')
            data = notification.get('data', {})

            logger.info(f'Apple webhook: type={notification_type}, subtype={subtype}')

            # Decode transaction info from its own JWS
            signed_transaction = data.get('signedTransactionInfo', '')
            if signed_transaction:
                transaction = self._decode_jws_payload(signed_transaction)
            else:
                transaction = None

            # Decode renewal info from its own JWS
            signed_renewal = data.get('signedRenewalInfo', '')
            if signed_renewal:
                renewal = self._decode_jws_payload(signed_renewal)
            else:
                renewal = None

            if not transaction:
                logger.info('Apple webhook: no transaction info')
                return Response(status=status.HTTP_200_OK)

            original_transaction_id = transaction.get('originalTransactionId', '')
            if not original_transaction_id:
                logger.info('Apple webhook: no originalTransactionId')
                return Response(status=status.HTTP_200_OK)

            purchase = InAppPurchase.objects.filter(
                dm.Q(original_transaction_id=original_transaction_id) |
                dm.Q(transaction_id=original_transaction_id)
            ).first()

            if not purchase:
                logger.info(f'Apple webhook: purchase not found for originalTransactionId={original_transaction_id}')
                return Response(status=status.HTTP_200_OK)

            product_id = transaction.get('productId', purchase.product_id)
            expires_date_ms = transaction.get('expiresDate', None)
            transaction_id = transaction.get('transactionId', purchase.transaction_id)

            # Update expires_at if we have it
            if expires_date_ms:
                expires_at_dt = timezone.datetime.fromtimestamp(
                    expires_date_ms / 1000, tz=timezone.utc
                )
            else:
                expires_at_dt = purchase.expires_at

            # Notification type handling
            if notification_type == 'SUBSCRIBED':
                purchase.is_active = True
                purchase.is_verified = True
                if expires_date_ms:
                    purchase.expires_at = expires_at_dt
                purchase.transaction_id = transaction_id
                purchase.product_id = product_id
                purchase.save()

                if purchase.user.plan != 'pro':
                    purchase.user.plan = 'pro'
                    purchase.user.save(update_fields=['plan'])
                logger.info(f'Apple webhook: activated subscription for user {purchase.user.id}')

            elif notification_type == 'DID_RENEW':
                purchase.is_active = True
                if expires_date_ms:
                    purchase.expires_at = expires_at_dt
                purchase.transaction_id = transaction_id
                purchase.save()
                logger.info(f'Apple webhook: renewed subscription for user {purchase.user.id}')

            elif notification_type == 'DID_RECOVER':
                purchase.is_active = True
                if expires_date_ms:
                    purchase.expires_at = expires_at_dt
                purchase.save()
                logger.info(f'Apple webhook: recovered subscription for user {purchase.user.id}')

            elif notification_type == 'DID_FAIL_TO_RENEW':
                logger.info(f'Apple webhook: subscription failed to renew for user {purchase.user.id}')

            elif notification_type == 'DID_CHANGE_RENEWAL_STATUS':
                auto_renew = renewal.get('autoRenewProductId', None) if renewal else None
                logger.info(f'Apple webhook: renewal status changed for user {purchase.user.id}, autoRenew={auto_renew}')

            elif notification_type == 'CANCEL':
                purchase.is_active = False
                purchase.save()
                if purchase.user.plan != 'free':
                    purchase.user.plan = 'free'
                    purchase.user.save(update_fields=['plan'])
                logger.info(f'Apple webhook: cancelled subscription for user {purchase.user.id}')

            elif notification_type == 'REFUND':
                purchase.is_active = False
                purchase.save()
                if purchase.user.plan != 'free':
                    purchase.user.plan = 'free'
                    purchase.user.save(update_fields=['plan'])
                logger.info(f'Apple webhook: refund for user {purchase.user.id}')

            elif notification_type == 'REVOKE':
                purchase.is_active = False
                purchase.save()
                if purchase.user.plan != 'free':
                    purchase.user.plan = 'free'
                    purchase.user.save(update_fields=['plan'])
                logger.info(f'Apple webhook: revoked for user {purchase.user.id}')

            elif notification_type == 'PRICE_INCREASE':
                logger.info(f'Apple webhook: price increase for user {purchase.user.id}')

            else:
                logger.info(f'Apple webhook: unhandled type={notification_type}')

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Apple webhook error: {e}', exc_info=True)
            return Response(status=status.HTTP_200_OK)


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

# IAP Server-Side Purchase Verification — Backend Contract

> **Base URL:** `https://api.heartbeatharmony.tech/api`
> **Auth:** All endpoints require a valid Bearer token (`Authorization: Bearer <access_token>`)

---

## Overview

The Flutter app uses the `in_app_purchase` package. After every successful purchase or restore, it immediately calls `POST /purchases/verify` to let the backend validate the receipt with Google / Apple. On every app launch it calls `GET /users/me/premium` to get the authoritative premium state.

```
User buys / restores a product
  └─► Google Play / App Store returns a receipt (PurchaseDetails)
        └─► App POSTs receipt ──► POST /api/purchases/verify
                                        └─► Backend calls Google Play API or Apple App Store API
                                              └─► Stores result in DB
                                                    └─► Returns { "is_premium": true, "expires_at": "..." }

App launches / after purchase
  └─► GET /api/users/me/premium
        └─► Returns { "is_premium": true/false, "expires_at": "..." }
              └─► App evaluates: is_premium && (expires_at is None OR expires_at > now)
```

---

## Product IDs

These are the exact strings the Flutter app sends in every `POST /purchases/verify` request.

| Plan | Platform | `product_id` |
|---|---|---|
| Monthly subscription | Android | `com.icsncardiology.premium.monthly` |
| Monthly subscription | iOS | `com.icsncardiology.heartbeatharmony.premium.monthly` |
| Lifetime one-time | Android | `com.icsncardiology.premium.lifetime` |
| Lifetime one-time | iOS | `com.icsncardiology.heartbeatharmony.premium.lifetime` |

> The monthly plan grants access for **30 days** from the purchase date.  
> Default prices: Monthly **$2.99** · Lifetime **$29.99**

---

## Endpoint 1 — Verify a Purchase

### `POST /api/purchases/verify`

Called by the Flutter app **immediately after** every successful purchase or restore event from the `in_app_purchase` purchase stream.

#### Request Body

```json
{
  "platform": "android",
  "product_id": "com.icsncardiology.premium.monthly",
  "purchase_token": "<serverVerificationData from in_app_purchase>",
  "transaction_id": "GPA.1234-5678-9012-34567"
}
```

| Field | Type | Notes |
|---|---|---|
| `platform` | `string` | `"android"` or `"ios"` — determines which store API to call |
| `product_id` | `string` | One of the four product IDs listed above |
| `purchase_token` | `string` | **Android:** `purchaseDetails.verificationData.serverVerificationData` (the raw Google Play purchase token). **iOS:** same field contains the base-64 App Store receipt |
| `transaction_id` | `string` | `purchaseDetails.purchaseID` — Android order ID (e.g. `GPA.xxx`) or iOS transaction ID. May be an empty string if unavailable |

#### How the Flutter app generates this payload

```dart
// From premium_repository.dart → PurchaseVerifyRequest.toJson()
{
  'platform': Platform.isAndroid ? 'android' : 'ios',
  'product_id': details.productID,         // e.g. "com.icsncardiology.premium.monthly"
  'purchase_token': details.verificationData.serverVerificationData,
  'transaction_id': details.purchaseID ?? '',
}
```

#### Success Response `200 OK` or `201 Created`

```json
{
  "is_premium": true,
  "expires_at": "2026-07-18T00:00:00Z"
}
```

| Field | Type | Notes |
|---|---|---|
| `is_premium` | `boolean` | `true` when the purchase is valid and active |
| `expires_at` | `string \| null` | ISO-8601 UTC. **`null` for lifetime purchases.** For monthly, set to `purchase_date + 30 days` |

> The Flutter app reads `data['is_premium']` from the response body.  
> A `200`/`201` with no JSON body is also treated as verified (`is_premium = true`).

#### Error Responses

| HTTP | `error` value | When to return |
|---|---|---|
| `400` | `"invalid_payload"` | Missing or malformed fields (`platform`, `product_id`, or `purchase_token` absent) |
| `402` | `"purchase_not_verified"` | The Google/Apple API rejected the receipt |
| `409` | `"already_verified"` | Same `purchase_token` already exists in DB — **safe to return `200` with the current stored status instead** |
| `500` | `"store_api_error"` | Google/Apple API is unreachable or returned an unexpected error |

> [!IMPORTANT]
> The Flutter app treats any non-2xx as a failed verification but **does not crash** — it logs the error and continues. The local `SharedPreferences` cache is the fallback. Always return a JSON body with an `"error"` key for non-2xx so errors are identifiable in logs.

---

## Endpoint 2 — Get Premium Status

### `GET /api/users/me/premium`

Called on **every app launch** and after every purchase. This is the **single source of truth** for whether the user has an active premium entitlement. The Bearer token identifies the user — no request body.

#### Response `200 OK`

```json
{
  "is_premium": true,
  "expires_at": "2026-07-18T00:00:00Z"
}
```

```json
{
  "is_premium": false,
  "expires_at": null
}
```

| Field | Type | Notes |
|---|---|---|
| `is_premium` | `boolean` | Whether the user has a currently active premium entitlement |
| `expires_at` | `string \| null` | ISO-8601 UTC expiry. `null` for lifetime purchases or non-premium users |

#### How the Flutter app evaluates the response

```dart
// From premium_repository.dart → PremiumStatus.isActive
bool get isActive {
  if (!isPremium) return false;
  if (expiresAt == null) return true;          // lifetime purchase
  return expiresAt!.isAfter(DateTime.now());   // monthly: check not expired
}
```

So the backend must set `expires_at` correctly — the app does **not** add any extra grace period.

#### Fallback behaviour

If this endpoint returns a network error (any exception / non-200), the Flutter app falls back to its local `SharedPreferences` IAP cache (`PremiumController._checkPremiumStatus`). **The app will never show a crash to the user due to this endpoint being down.**

---

## Python Backend Implementation

### Django / DRF example

```python
# models.py
import uuid
from django.db import models
from django.conf import settings

class UserPurchase(models.Model):
    PLATFORM_CHOICES = [('android', 'Android'), ('ios', 'iOS')]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='purchases')
    platform       = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    product_id     = models.CharField(max_length=255)
    purchase_token = models.TextField(unique=True)   # UNIQUE — prevents duplicate grants
    transaction_id = models.CharField(max_length=255, blank=True)
    is_verified    = models.BooleanField(default=False)
    expires_at     = models.DateTimeField(null=True, blank=True)  # None = lifetime
    raw_store_resp = models.JSONField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'is_verified', 'expires_at'])]
```

```python
# serializers.py
from rest_framework import serializers

class PurchaseVerifySerializer(serializers.Serializer):
    platform       = serializers.ChoiceField(choices=['android', 'ios'])
    product_id     = serializers.CharField()
    purchase_token = serializers.CharField()
    transaction_id = serializers.CharField(allow_blank=True, default='')

class PremiumStatusSerializer(serializers.Serializer):
    is_premium = serializers.BooleanField()
    expires_at = serializers.DateTimeField(allow_null=True)
```

```python
# views.py
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import UserPurchase
from .serializers import PurchaseVerifySerializer, PremiumStatusSerializer
from .store_clients import verify_android_purchase, verify_ios_purchase

MONTHLY_PRODUCT_IDS = {
    'com.icsncardiology.premium.monthly',
    'com.icsncardiology.heartbeatharmony.premium.monthly',
}
LIFETIME_PRODUCT_IDS = {
    'com.icsncardiology.premium.lifetime',
    'com.icsncardiology.heartbeatharmony.premium.lifetime',
}
MONTHLY_DURATION_DAYS = 30


class VerifyPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PurchaseVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'invalid_payload', 'details': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data    = serializer.validated_data
        platform       = data['platform']
        product_id     = data['product_id']
        purchase_token = data['purchase_token']
        transaction_id = data['transaction_id']

        # Idempotency — same token already stored
        existing = UserPurchase.objects.filter(purchase_token=purchase_token).first()
        if existing:
            is_active = existing.is_verified and (
                existing.expires_at is None or existing.expires_at > timezone.now()
            )
            return Response(
                PremiumStatusSerializer({
                    'is_premium': is_active,
                    'expires_at': existing.expires_at,
                }).data,
                status=status.HTTP_200_OK,
            )

        # Verify with the store
        # store_clients return (verified, raw_resp, expires_at)
        # expires_at comes from the store API response (expiryTimeMillis / expires_date_ms)
        # — the Flutter app never sends expires_at.
        try:
            if platform == 'android':
                verified, raw_resp, expires_at = verify_android_purchase(product_id, purchase_token)
            else:
                verified, raw_resp, expires_at = verify_ios_purchase(purchase_token)
        except Exception as e:
            return Response({'error': 'store_api_error', 'detail': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not verified:
            return Response({'error': 'purchase_not_verified'},
                            status=status.HTTP_402_PAYMENT_REQUIRED)

        # Fallback: if the store API didn't return an expiry (e.g. lifetime one-time
        # products never have an expiryTimeMillis), keep expires_at = None.
        # For monthly: the store always provides it, but if somehow missing, compute it.
        if expires_at is None and product_id in MONTHLY_PRODUCT_IDS:
            expires_at = timezone.now() + timedelta(days=MONTHLY_DURATION_DAYS)

        UserPurchase.objects.create(
            user=request.user,
            platform=platform,
            product_id=product_id,
            purchase_token=purchase_token,
            transaction_id=transaction_id,
            is_verified=True,
            expires_at=expires_at,      # from store API, not from the app
            raw_store_resp=raw_resp,
        )

        return Response(
            PremiumStatusSerializer({'is_premium': True, 'expires_at': expires_at}).data,
            status=status.HTTP_201_CREATED,
        )


class PremiumStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        purchase = (
            UserPurchase.objects
            .filter(user=request.user, is_verified=True)
            .filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now()))
            .order_by('-created_at')
            .first()
        )
        if purchase:
            return Response(
                PremiumStatusSerializer({
                    'is_premium': True,
                    'expires_at': purchase.expires_at,
                }).data
            )
        return Response(PremiumStatusSerializer({'is_premium': False, 'expires_at': None}).data)
```

```python
# urls.py
from django.urls import path
from .views import VerifyPurchaseView, PremiumStatusView

urlpatterns = [
    path('purchases/verify',   VerifyPurchaseView.as_view(), name='iap-verify'),
    path('users/me/premium',   PremiumStatusView.as_view(), name='iap-premium-status'),
]
```

### Store Verification Clients

> [!IMPORTANT]
> The Flutter app **never sends `expires_at`**. Your backend must extract it from the
> Google Play / App Store API response. Both functions below return a **3-tuple**
> `(verified, raw_response, expires_at)` so the view can store the store-authoritative expiry.

```python
# store_clients.py
import time
import requests
from datetime import datetime, timezone as tz
from google.oauth2 import service_account
from googleapiclient.discovery import build

ANDROID_PACKAGE_NAME = 'com.icsncardiology'   # your app's package name


def verify_android_purchase(
    product_id: str,
    purchase_token: str,
) -> tuple[bool, dict, datetime | None]:
    """
    Calls the Google Play Developer API.
    Returns (verified, raw_response, expires_at).

    expires_at source:
      - Subscriptions  → resp['expiryTimeMillis']  (ms UTC from Google)
      - One-time / lifetime → None (no expiry in Google response)

    Requires a service account JSON key with the 'Financial data viewer' role
    in Play Console → Setup → API access.
    """
    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service_account.json',
        scopes=['https://www.googleapis.com/auth/androidpublisher'],
    )
    service = build('androidpublisher', 'v3', credentials=credentials)

    if 'monthly' in product_id:
        # ── Subscription ──────────────────────────────────────────────────────
        resp = service.purchases().subscriptions().get(
            packageName=ANDROID_PACKAGE_NAME,
            subscriptionId=product_id,
            token=purchase_token,
        ).execute()

        # Google returns expiryTimeMillis as a string of milliseconds
        expiry_ms  = int(resp.get('expiryTimeMillis', 0))
        now_ms     = int(time.time() * 1000)
        verified   = expiry_ms > now_ms
        expires_at = (
            datetime.utcfromtimestamp(expiry_ms / 1000).replace(tzinfo=tz.utc)
            if expiry_ms else None
        )
    else:
        # ── Lifetime one-time product ─────────────────────────────────────────
        resp = service.purchases().products().get(
            packageName=ANDROID_PACKAGE_NAME,
            productId=product_id,
            token=purchase_token,
        ).execute()
        # purchaseState: 0 = purchased, 1 = cancelled, 2 = pending
        verified   = resp.get('purchaseState') == 0
        expires_at = None   # lifetime — no expiry

    return verified, resp, expires_at


def verify_ios_purchase(
    purchase_token: str,
) -> tuple[bool, dict, 'datetime | None']:
    """
    Verifies an App Store receipt (base-64) using the App Store verifyReceipt API.
    Returns (verified, raw_response, expires_at).

    expires_at source:
      - Subscriptions  → latest_receipt_info[*]['expires_date_ms']  (ms UTC from Apple)
      - Lifetime       → None  (one-time products have no expires_date_ms)

    Always tries production first; retries sandbox on status 21007.
    """
    import os
    shared_secret = os.environ['APPLE_SHARED_SECRET']
    payload = {
        'receipt-data': purchase_token,
        'password': shared_secret,
        'exclude-old-transactions': True,
    }

    prod_url    = 'https://buy.itunes.apple.com/verifyReceipt'
    sandbox_url = 'https://sandbox.itunes.apple.com/verifyReceipt'

    resp = requests.post(prod_url, json=payload, timeout=10)
    data = resp.json()

    if data.get('status') == 21007:   # sandbox receipt sent to production
        resp = requests.post(sandbox_url, json=payload, timeout=10)
        data = resp.json()

    if data.get('status') != 0:
        return False, data, None

    now_ms   = int(time.time() * 1000)
    receipts = data.get('latest_receipt_info', [])

    if receipts:
        # Pick the receipt line with the furthest expiry
        latest   = max(receipts, key=lambda r: int(r.get('expires_date_ms', 0)))
        expiry_ms = int(latest.get('expires_date_ms', 0))
        verified  = expiry_ms > now_ms
        expires_at = (
            datetime.utcfromtimestamp(expiry_ms / 1000).replace(tzinfo=tz.utc)
            if expiry_ms else None
        )
    else:
        # No receipt lines → lifetime product (no expiry in App Store response)
        verified   = True
        expires_at = None

    return verified, data, expires_at
```

---

## Database Schema (PostgreSQL / Django migrations)

```sql
CREATE TABLE iap_userpurchase (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
  platform         VARCHAR(10)  NOT NULL,           -- 'android' | 'ios'
  product_id       VARCHAR(255) NOT NULL,
  purchase_token   TEXT         NOT NULL UNIQUE,    -- prevents duplicate grants
  transaction_id   VARCHAR(255) DEFAULT '',
  is_verified      BOOLEAN      DEFAULT FALSE,
  expires_at       TIMESTAMPTZ,                     -- NULL = lifetime
  raw_store_resp   JSONB,
  created_at       TIMESTAMPTZ  DEFAULT NOW(),
  updated_at       TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX idx_iap_user_active ON iap_userpurchase (
  user_id, is_verified, expires_at
);
```

**Premium status query:**
```sql
SELECT EXISTS (
  SELECT 1 FROM iap_userpurchase
  WHERE user_id   = %s
    AND is_verified = TRUE
    AND (expires_at IS NULL OR expires_at > NOW())
) AS is_premium;
```

---

## Security Requirements

> [!CAUTION]
> Never trust the client to self-report `is_premium`. The Flutter app sends a raw receipt — the **server must always verify it with Google/Apple before granting access**.

- [ ] Rate-limit `POST /purchases/verify` — suggested: 10 req/min per user.
- [ ] The `purchase_token` column has a `UNIQUE` constraint to prevent double-grant attacks.
- [ ] Never expose the Google service account JSON key or Apple shared secret in any client or public repo.
- [ ] Log all verification attempts (success and failure) with `user_id`, `platform`, `product_id`, HTTP status from the store API.
- [ ] Return `409` (or `200` with current status) when the same token is resubmitted — do **not** grant a second entitlement.
- [ ] Store `raw_store_resp` (the full Google/Apple API response) for audit and dispute resolution.

---

## Flutter App Files Reference

| File | Role |
|---|---|
| [`iap_config.dart`](file:///Volumes/New%20Volume/Development/Projects/heartbeat_harmony/lib/core/config/iap_config.dart) | Product IDs, prices, `monthlyDurationDays = 30`, `storageKey` |
| [`endpoints.dart`](file:///Volumes/New%20Volume/Development/Projects/heartbeat_harmony/lib/core/service/network/endpoints.dart) | `verifyPurchase = '/purchases/verify'`, `getPremiumStatus = '/users/me/premium'` |
| [`premium_repository.dart`](file:///Volumes/New%20Volume/Development/Projects/heartbeat_harmony/lib/core/service/iap/premium_repository.dart) | `PurchaseVerifyRequest` / `PremiumStatus` models; `verifyAndStorePurchase()` + `fetchPremiumStatus()` |
| [`iap_service.dart`](file:///Volumes/New%20Volume/Development/Projects/heartbeat_harmony/lib/core/service/iap/iap_service.dart) | Listens to the purchase stream; calls `_verifyWithBackend()` fire-and-forget on every successful event |
| [`premium_controller.dart`](file:///Volumes/New%20Volume/Development/Projects/heartbeat_harmony/lib/core/service/iap/premium_controller.dart) | Calls `GET /users/me/premium` on launch; falls back to local cache on any network error |

---

## Testing Checklist

- [ ] `POST /purchases/verify` with a valid Android purchase token → `201` `{ "is_premium": true, "expires_at": "<30 days from now>" }`
- [ ] `POST /purchases/verify` with a valid iOS receipt → `201` `{ "is_premium": true, ... }`
- [ ] `POST /purchases/verify` with a lifetime product → `201` `{ "is_premium": true, "expires_at": null }`
- [ ] `POST /purchases/verify` with a tampered / fake token → `402` `{ "error": "purchase_not_verified" }`
- [ ] `POST /purchases/verify` with the same token twice → `200` with current status (idempotent)
- [ ] `GET /users/me/premium` for an active subscriber → `{ "is_premium": true, "expires_at": "..." }`
- [ ] `GET /users/me/premium` for a non-premium user → `{ "is_premium": false, "expires_at": null }`
- [ ] `GET /users/me/premium` for an expired monthly → `{ "is_premium": false, "expires_at": "<past date>" }`
- [ ] `GET /users/me/premium` for a lifetime purchase → `{ "is_premium": true, "expires_at": null }`
- [ ] Both endpoints return `401` when called without a Bearer token

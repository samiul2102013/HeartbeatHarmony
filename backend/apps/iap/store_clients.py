import json
import time
from datetime import datetime, timezone as tz
from urllib.request import Request, urlopen
from urllib.error import URLError

from django.conf import settings

# ── Shared ──────────────────────────────────────────────────────────────────

MONTHLY_PRODUCT_IDS = {
    'com.icsncardiology.premium.monthly',
    'com.icsncardiology.heartbeatharmony.premium.monthly',
}
LIFETIME_PRODUCT_IDS = {
    'com.icsncardiology.premium.lifetime',
    'com.icsncardiology.heartbeatharmony.premium.lifetime',
}
VALID_PRODUCT_IDS = MONTHLY_PRODUCT_IDS | LIFETIME_PRODUCT_IDS
MONTHLY_DURATION_DAYS = 30

# ── Android Google Play Store (via service account) ─────────────────────────

ANDROID_PACKAGE_NAME = 'com.icsncardiology'


def _get_google_access_token():
    """Create a JWT assertion and exchange it for a Google OAuth2 access token
    using the service account JSON key file specified in settings."""
    import jwt as pyjwt

    import base64 as _b64
    key_json = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_KEY_JSON', None)
    if key_json:
        try:
            sa_info = json.loads(key_json)
        except json.JSONDecodeError:
            sa_info = json.loads(_b64.b64decode(key_json).decode())
    else:
        key_path = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_KEY_PATH', None)
        if not key_path:
            raise RuntimeError('GOOGLE_SERVICE_ACCOUNT_KEY_PATH or GOOGLE_SERVICE_ACCOUNT_KEY_JSON not set')
        with open(key_path) as f:
            sa_info = json.load(f)

    now = int(time.time())
    assertion = pyjwt.encode({
        'iss': sa_info['client_email'],
        'scope': 'https://www.googleapis.com/auth/androidpublisher',
        'aud': 'https://oauth2.googleapis.com/token',
        'iat': now,
        'exp': now + 3600,
    }, sa_info['private_key'], algorithm='RS256')

    body = json.dumps({
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': assertion,
    }).encode()

    req = Request('https://oauth2.googleapis.com/token', data=body,
                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
    resp = json.loads(urlopen(req, timeout=10).read())
    return resp['access_token']


def _google_api_get(path, access_token):
    req = Request(f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{ANDROID_PACKAGE_NAME}/{path}',
                  headers={'Authorization': f'Bearer {access_token}'})
    return json.loads(urlopen(req, timeout=10).read())


def verify_android_purchase(
    product_id: str,
    purchase_token: str,
) -> tuple[bool, dict | None, str | None]:
    """Verify an Android purchase with the Google Play Developer API.

    Returns (verified, raw_response, expires_at).
    expires_at is an ISO-8601 UTC string for subscriptions, None for lifetime.
    """
    try:
        token = _get_google_access_token()
    except Exception as e:
        return False, None, None

    try:
        if product_id in MONTHLY_PRODUCT_IDS:
            resp = _google_api_get(
                f'purchases/subscriptions/{product_id}/tokens/{purchase_token}',
                token,
            )
            expiry_ms = int(resp.get('expiryTimeMillis', 0))
            now_ms = int(time.time() * 1000)
            verified = expiry_ms > now_ms
            expires_at = (
                datetime.utcfromtimestamp(expiry_ms / 1000).strftime('%Y-%m-%dT%H:%M:%SZ')
                if expiry_ms else None
            )
        else:
            resp = _google_api_get(
                f'purchases/products/{product_id}/tokens/{purchase_token}',
                token,
            )
            verified = resp.get('purchaseState') == 0
            expires_at = None

        return verified, resp, expires_at
    except URLError:
        return False, None, None


# ── iOS App Store (via Apple verifyReceipt API) ─────────────────────────────

APPLE_PRODUCTION_URL = 'https://buy.itunes.apple.com/verifyReceipt'
APPLE_SANDBOX_URL = 'https://sandbox.itunes.apple.com/verifyReceipt'


def verify_ios_purchase(
    receipt_data: str,
) -> tuple[bool, dict | None, str | None]:
    """Verify an iOS receipt with the App Store verifyReceipt API.

    Returns (verified, raw_response, expires_at).
    expires_at is an ISO-8601 UTC string for subscriptions, None for lifetime.
    """
    shared_secret = getattr(settings, 'APPLE_SHARED_SECRET', None)
    if not shared_secret:
        return False, None, None

    payload = json.dumps({
        'receipt-data': receipt_data,
        'password': shared_secret,
        'exclude-old-transactions': True,
    }).encode('utf-8')

    def _post(url):
        req = Request(url, data=payload, headers={'Content-Type': 'application/json'})
        return json.loads(urlopen(req, timeout=15).read().decode('utf-8'))

    try:
        data = _post(APPLE_PRODUCTION_URL)
    except URLError:
        return False, None, None

    if data.get('status') == 21007:
        try:
            data = _post(APPLE_SANDBOX_URL)
        except URLError:
            return False, None, None

    if data.get('status') != 0:
        return False, data, None

    receipts = data.get('latest_receipt_info', [])

    if receipts:
        latest = max(receipts, key=lambda r: int(r.get('expires_date_ms', 0)))
        expiry_ms = int(latest.get('expires_date_ms', 0))
        now_ms = int(time.time() * 1000)
        verified = expiry_ms > now_ms
        expires_at = (
            datetime.utcfromtimestamp(expiry_ms / 1000).strftime('%Y-%m-%dT%H:%M:%SZ')
            if expiry_ms else None
        )
    else:
        verified = True
        expires_at = None

    return verified, data, expires_at

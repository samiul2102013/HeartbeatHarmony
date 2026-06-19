import json
import logging
import time
from datetime import datetime, timezone as tz
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.conf import settings

logger = logging.getLogger(__name__)

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

ANDROID_PACKAGE_NAME = 'com.icsncardiology.heartbeatharmony'


def _get_google_access_token():
    """Obtain a Google OAuth2 access token for the Android Publisher API
    using the service account JSON key."""
    import base64 as _b64
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as GoogleRequest

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

    try:
        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=['https://www.googleapis.com/auth/androidpublisher'],
        )
        creds.refresh(GoogleRequest())
        logger.info('Google OAuth token obtained successfully')
        return creds.token
    except Exception as e:
        logger.error(f'Failed to get Google access token: {e}', exc_info=True)
        raise


def _google_api_get(path, access_token):
    url = f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{ANDROID_PACKAGE_NAME}/{path}'
    req = Request(url, headers={'Authorization': f'Bearer {access_token}'})
    try:
        resp = json.loads(urlopen(req, timeout=10).read())
        return resp
    except HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        logger.error(f'Google Play API error {e.code} for {url}: {error_body}')
        raise
    except Exception as e:
        logger.error(f'Google Play API unexpected error: {e}', exc_info=True)
        raise


def _google_api_post(path, access_token, body=None):
    url = f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{ANDROID_PACKAGE_NAME}/{path}'
    data = json.dumps(body).encode('utf-8') if body else b''
    req = Request(url, data=data or None, headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'})
    req.method = 'POST'
    try:
        resp = urlopen(req, timeout=10).read()
        return json.loads(resp) if resp else {}
    except HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        logger.error(f'Google Play API error {e.code} for {url}: {error_body}')
        raise
    except Exception as e:
        logger.error(f'Google Play API unexpected error: {e}', exc_info=True)
        raise


def cancel_android_subscription(purchase_token, product_id):
    """Cancel an Android subscription via Google Play API.
    The subscription continues until the end of the current billing period."""
    try:
        token = _get_google_access_token()
    except Exception as e:
        logger.error(f'Failed to get Google access token for cancel: {e}', exc_info=True)
        raise

    try:
        logger.info(f'Cancelling Android subscription: {product_id}')
        _google_api_post(
            f'purchases/subscriptions/{product_id}/tokens/{purchase_token}:cancel',
            token,
        )
        logger.info(f'Android subscription cancelled successfully: {product_id}')
    except HTTPError as e:
        logger.error(f'Google Play API cancel error: {e}')
        raise
    except Exception as e:
        logger.error(f'Google Play API cancel unexpected error: {e}', exc_info=True)
        raise


def cancel_ios_subscription(original_transaction_id):
    """Cancel an iOS subscription via App Store Server API.
    Sets autoRenewStatus to 0 — user keeps access until expiry."""
    shared_secret = getattr(settings, 'APPLE_SHARED_SECRET', None)
    if not shared_secret:
        raise RuntimeError('APPLE_SHARED_SECRET not set')

    from urllib.request import Request as URLRequest
    import json

    body = json.dumps({'autoRenewStatus': 0}).encode('utf-8')
    url = f'https://api.storekit-sandbox.itunes.apple.com/inApps/v1/subscriptions/{original_transaction_id}'
    req = URLRequest(url, data=body, headers={'Content-Type': 'application/json'})
    req.method = 'PUT'

    try:
        urlopen(req, timeout=15)
        logger.info(f'iOS subscription cancelled successfully: {original_transaction_id}')
    except HTTPError as e:
        logger.error(f'App Store cancel API error {e.code}: {e.read().decode(errors=\"replace\")}')
        raise
    except Exception as e:
        logger.error(f'App Store cancel API unexpected error: {e}', exc_info=True)
        raise


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
        logger.error(f'Failed to get Google access token: {e}', exc_info=True)
        return False, None, None

    try:
        if product_id in MONTHLY_PRODUCT_IDS:
            logger.info(f'Verifying Android subscription: {product_id}')
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
            logger.info(f'Subscription response: expiry_ms={expiry_ms}, now_ms={now_ms}, verified={verified}')
        else:
            logger.info(f'Verifying Android product (lifetime): {product_id}')
            resp = _google_api_get(
                f'purchases/products/{product_id}/tokens/{purchase_token}',
                token,
            )
            purchase_state = resp.get('purchaseState')
            verified = purchase_state == 0
            expires_at = None
            logger.info(f'Product response: purchaseState={purchase_state}, verified={verified}')

        return verified, resp, expires_at
    except HTTPError as e:
        logger.error(f'Google Play API HTTP error: {e}')
        return False, None, None
    except Exception as e:
        logger.error(f'Google Play API unexpected error: {e}', exc_info=True)
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

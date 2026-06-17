import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from django.conf import settings

APPLE_PRODUCTION_URL = 'https://buy.itunes.apple.com/verifyReceipt'
APPLE_SANDBOX_URL = 'https://sandbox.itunes.apple.com/verifyReceipt'

MONTHLY_PRODUCT_ID = 'com.icsncardiology.heartbeatharmony.premium.monthly'
LIFETIME_PRODUCT_ID = 'com.icsncardiology.heartbeatharmony.premium.lifetime'

VALID_PRODUCT_IDS = {MONTHLY_PRODUCT_ID, LIFETIME_PRODUCT_ID}


class AppleValidationError(Exception):
    pass


def _post_to_apple(url, receipt_data, shared_secret):
    body = json.dumps({
        'receipt-data': receipt_data,
        'password': shared_secret,
        'exclude-old-transactions': True,
    }).encode('utf-8')

    req = Request(url, data=body, headers={'Content-Type': 'application/json'})
    try:
        resp = urlopen(req, timeout=15)
        return json.loads(resp.read().decode('utf-8'))
    except URLError as e:
        raise AppleValidationError(f'Apple server error: {e}')


def validate_apple_receipt(receipt_data):
    shared_secret = getattr(settings, 'APPLE_SHARED_SECRET', None)
    if not shared_secret:
        raise AppleValidationError('Apple shared secret not configured')

    result = _post_to_apple(APPLE_PRODUCTION_URL, receipt_data, shared_secret)
    status = result.get('status')

    # 21007 = sandbox receipt sent to production → retry sandbox
    if status == 21007:
        result = _post_to_apple(APPLE_SANDBOX_URL, receipt_data, shared_secret)
        status = result.get('status')

    if status != 0:
        error_map = {
            21000: 'Bad App Store request',
            21002: 'Malformed receipt data',
            21003: 'Receipt could not be authenticated',
            21004: 'Shared secret mismatch',
            21005: 'Receipt server unavailable',
            21006: 'Receipt is expired',
            21008: 'Production receipt sent to sandbox',
            21010: 'Access forbidden',
            21100: 'Internal data access error',
            21199: 'Unknown error',
        }
        raise AppleValidationError(error_map.get(status, f'Unknown status {status}'))

    environment = result.get('environment', 'Production')
    latest_receipt_info = result.get('latest_receipt_info', [])
    receipt = result.get('receipt', {})
    in_app = receipt.get('in_app', [])

    return {
        'environment': environment,
        'latest_receipt_info': latest_receipt_info,
        'in_app': in_app,
    }


def extract_purchase_info(validation_result):
    environment = validation_result['environment']
    latest = validation_result['latest_receipt_info']
    in_app = validation_result['in_app']

    purchases = []

    # Process subscriptions from latest_receipt_info
    for entry in latest:
        product_id = entry.get('product_id')
        if product_id not in VALID_PRODUCT_IDS:
            continue

        if product_id == LIFETIME_PRODUCT_ID:
            purchases.append({
                'product_id': product_id,
                'purchase_type': 'lifetime',
                'original_transaction_id': entry.get('original_transaction_id'),
                'transaction_id': entry.get('transaction_id'),
                'purchase_date': entry.get('purchase_date'),
                'expires_at': None,
                'environment': environment,
                'is_active': True,
            })
        else:
            expires_date = entry.get('expires_date')
            cancellation = entry.get('cancellation_date')
            is_active = not cancellation and (
                entry.get('in_app_ownership_type') != 'PURCHASED'
            )
            purchases.append({
                'product_id': product_id,
                'purchase_type': 'subscription',
                'original_transaction_id': entry.get('original_transaction_id'),
                'transaction_id': entry.get('transaction_id'),
                'purchase_date': entry.get('purchase_date'),
                'expires_at': expires_date,
                'environment': environment,
                'is_active': is_active,
            })

    # Process lifetime purchases from in_app array
    for entry in in_app:
        product_id = entry.get('product_id')
        if product_id not in VALID_PRODUCT_IDS:
            continue
        # Avoid duplicates already in latest_receipt_info
        oid = entry.get('original_transaction_id')
        if any(p['original_transaction_id'] == oid for p in purchases):
            continue
        purchases.append({
            'product_id': product_id,
            'purchase_type': 'lifetime' if product_id == LIFETIME_PRODUCT_ID else 'subscription',
            'original_transaction_id': oid,
            'transaction_id': entry.get('transaction_id'),
            'purchase_date': entry.get('purchase_date'),
            'expires_at': None,
            'environment': environment,
            'is_active': True,
        })

    return purchases

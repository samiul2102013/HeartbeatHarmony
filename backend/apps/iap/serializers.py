from rest_framework import serializers


class PurchaseVerifySerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=['android', 'ios'])
    product_id = serializers.CharField()
    purchase_token = serializers.CharField()
    transaction_id = serializers.CharField(allow_blank=True, default='')


class PremiumStatusSerializer(serializers.Serializer):
    is_premium = serializers.BooleanField()
    expires_at = serializers.DateTimeField(allow_null=True)

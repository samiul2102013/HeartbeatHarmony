from rest_framework import serializers


class VerifyReceiptSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=['ios'])
    receipt = serializers.CharField(help_text="Base64-encoded receipt data from Apple")


class RestoreReceiptSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=['ios'])
    receipt = serializers.CharField(help_text="Base64-encoded receipt data from Apple")


class PremiumStatusSerializer(serializers.Serializer):
    isPremium = serializers.BooleanField()
    productId = serializers.CharField(allow_null=True)
    purchaseType = serializers.CharField(allow_null=True)
    expiresAt = serializers.DateTimeField(allow_null=True)

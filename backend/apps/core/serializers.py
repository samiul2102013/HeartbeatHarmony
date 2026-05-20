from rest_framework import serializers

from .models import ContentPage, FAQ, SupportContact


class ContentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPage
        fields = ['slug', 'title', 'content', 'updated_at']


class AdminContentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPage
        fields = ['id', 'slug', 'title', 'content', 'is_active', 'created_at', 'updated_at']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order']


class AdminFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order', 'is_active']


class SupportContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportContact
        fields = ['email', 'phone']


class AdminSupportContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportContact
        fields = ['id', 'email', 'phone']

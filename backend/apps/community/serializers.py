from rest_framework import serializers
from .models import CommunityMessage, DirectMessage
from apps.accounts.models import User


class CommunityMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)

    class Meta:
        model = CommunityMessage
        fields = [
            'id', 'sender', 'sender_id', 'sender_username', 'sender_avatar',
            'content', 'file', 'message_type', 'created_at',
        ]
        read_only_fields = [
            'id', 'sender', 'sender_id', 'sender_username', 'sender_avatar', 'created_at',
        ]


class CommunityMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True, default='')
    message_type = serializers.ChoiceField(
        choices=CommunityMessage.MessageType.choices,
        required=False,
        default=CommunityMessage.MessageType.TEXT,
    )
    file = serializers.FileField(required=False, allow_null=True)


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_id = serializers.IntegerField(source='receiver.id', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = DirectMessage
        fields = [
            'id', 'sender', 'sender_id', 'sender_username',
            'receiver', 'receiver_id', 'receiver_username',
            'content', 'is_read', 'created_at',
        ]
        read_only_fields = [
            'id', 'sender', 'sender_id', 'sender_username',
            'receiver', 'receiver_id', 'receiver_username', 'is_read', 'created_at',
        ]


class DirectMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


class UserListSerializer(serializers.ModelSerializer):
    """For DM user picker — list of other users."""
    class Meta:
        model = User
        fields = ['id', 'username', 'institute_name', 'first_name', 'last_name', 'avatar']
from rest_framework import serializers

from .models import Mood, CheckIn


def _abs_url(request, file_field):
    """Return absolute URL for a FileField, or None if no file."""
    if not file_field:
        return None
    try:
        url = file_field.url
    except (ValueError, AttributeError):
        return None
    if request is not None:
        return request.build_absolute_uri(url)
    return url


class MoodSerializer(serializers.ModelSerializer):
    svg = serializers.SerializerMethodField()

    class Meta:
        model = Mood
        fields = ['id', 'name', 'emoji', 'svg', 'score', 'is_active']

    def get_svg(self, obj):
        return _abs_url(self.context.get('request'), obj.svg)


class CheckInSerializer(serializers.ModelSerializer):
    mood_detail = MoodSerializer(source='mood', read_only=True)

    class Meta:
        model = CheckIn
        fields = [
            'id', 'mood', 'mood_detail',
            'mental_clarity', 'emotional_balance',
            'spiritual_wellness', 'physical_energy',
            'gratitude', 'notes',
            'heart_balance_score', 'created_at',
        ]
        read_only_fields = ['id', 'heart_balance_score', 'created_at', 'mood_detail']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CheckInSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views / history."""
    mood_name = serializers.CharField(source='mood.name', read_only=True)
    mood_emoji = serializers.CharField(source='mood.emoji', read_only=True)
    details = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        fields = [
            'id', 'mood_name', 'mood_emoji',
            'heart_balance_score', 'created_at',
            'details',
        ]

    def get_details(self, obj):
        return {
            'mental_clarity': obj.mental_clarity,
            'emotional_balance': obj.emotional_balance,
            'spiritual_wellness': obj.spiritual_wellness,
            'physical_energy': obj.physical_energy,
            'gratitude': obj.gratitude,
            'notes': obj.notes,
        }


# ── Admin serializers ─────────────────────────────────────────

class AdminMoodSerializer(serializers.ModelSerializer):
    svg = serializers.SerializerMethodField()

    class Meta:
        model = Mood
        fields = '__all__'

    def get_svg(self, obj):
        return _abs_url(self.context.get('request'), obj.svg)

    def to_internal_value(self, data):
        # Frontend may send the image file under 'emoji' or 'svg' key.
        # Accept both for backward compatibility.
        if 'emoji' in data and 'svg' not in data:
            emoji_val = data.get('emoji')
            if hasattr(emoji_val, 'read'):
                data = data.copy()
                data['svg'] = data.pop('emoji')
        return super().to_internal_value(data)


class AdminCheckInSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    mood_name = serializers.CharField(source='mood.name', read_only=True)

    class Meta:
        model = CheckIn
        fields = [
            'id', 'user', 'user_username', 'mood', 'mood_name',
            'mental_clarity', 'emotional_balance',
            'spiritual_wellness', 'physical_energy',
            'gratitude', 'notes', 'heart_balance_score', 'created_at',
        ]
        read_only_fields = ['heart_balance_score', 'created_at']
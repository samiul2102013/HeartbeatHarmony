from django.utils import timezone
from rest_framework import serializers
from .models import Category, Habit, HabitCompletion, HabitTemplate, FREE_HABIT_LIMIT, DAILY_COMPLETION_LIMIT, BYPASS_PRO_LIMITS


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active']


class HabitTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = HabitTemplate
        fields = [
            'id', 'category', 'category_name',
            'activity_name', 'description', 'duration',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class HabitSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    template_id = serializers.IntegerField(write_only=True, required=False)
    activity_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    duration = serializers.IntegerField(required=False, min_value=1)
    schedule_time = serializers.TimeField(source='reminder_time', required=False, allow_null=True)
    reminder_time = serializers.TimeField(write_only=True, required=False, allow_null=True)
    is_completed_today = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'category', 'category_detail',
            'activity_name', 'description', 'duration',
            'is_active', 'schedule_time', 'reminder_time', 'is_completed_today',
            'created_at', 'updated_at', 'template_id',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_detail', 'is_completed_today']

    def get_is_completed_today(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        today = timezone.localdate()
        return HabitCompletion.objects.filter(
            user=request.user, habit=obj, completed_date=today
        ).exists()

    def validate(self, attrs):
        request = self.context['request']
        user = self.context.get('resolved_user') or request.user
        template_id = attrs.pop('template_id', None)
        legacy_reminder_time = attrs.pop('reminder_time', None)

        # Backward compatibility: accept `reminder_time` from old clients,
        # but keep `schedule_time` as the canonical API field.
        if legacy_reminder_time is not None and attrs.get('reminder_time') is None:
            attrs['reminder_time'] = legacy_reminder_time

        # If template_id provided, copy template data
        if template_id and self.instance is None:
            try:
                template = HabitTemplate.objects.get(pk=template_id, is_active=True)
                attrs['category'] = template.category
                attrs['activity_name'] = template.activity_name
                attrs['description'] = template.description
                attrs['duration'] = template.duration
            except HabitTemplate.DoesNotExist:
                raise serializers.ValidationError({'template_id': 'Template not found.'})
        else:
            # No template: require manual fields
            if not attrs.get('activity_name') or not str(attrs.get('activity_name', '')).strip():
                raise serializers.ValidationError({'activity_name': 'This field is required.'})

        # Enforce free limit on create only (bypassed during testing)
        if not BYPASS_PRO_LIMITS and self.instance is None and not user.is_pro:
            active_count = Habit.objects.filter(user=user, is_active=True).count()
            if active_count >= FREE_HABIT_LIMIT:
                raise serializers.ValidationError(
                    f'Free plan allows up to {FREE_HABIT_LIMIT} habits. Upgrade to Pro for unlimited habits.'
                )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context.get('resolved_user') or self.context['request'].user
        return super().create(validated_data)


class HabitSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    schedule_time = serializers.TimeField(source='reminder_time', read_only=True)
    is_completed_today = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'activity_name', 'description',
            'category_name', 'category_icon', 'duration', 'is_active', 'schedule_time',
            'is_completed_today', 'created_at',
        ]

    def get_is_completed_today(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        today = timezone.localdate()
        return HabitCompletion.objects.filter(
            user=request.user, habit=obj, completed_date=today
        ).exists()


class HabitReminderSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'activity_name', 'description', 'duration',
            'category_name', 'category_icon', 'reminder_time',
            'is_active', 'created_at',
        ]


class HabitCompletionSerializer(serializers.ModelSerializer):
    habit_name = serializers.CharField(source='habit.activity_name', read_only=True)
    category_name = serializers.CharField(source='habit.category.name', read_only=True)

    class Meta:
        model = HabitCompletion
        fields = ['id', 'habit', 'habit_name', 'category_name', 'completed_date', 'created_at']
        read_only_fields = ['id', 'completed_date', 'created_at']


# ── Admin serializers ─────────────────────────────────────────

class AdminCategorySerializer(serializers.ModelSerializer):
    habit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active', 'habit_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        value = value.strip()
        queryset = Category.objects.filter(name__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('A category with this name already exists.')
        return value

    def create(self, validated_data):
        validated_data['name'] = validated_data['name'].strip()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            validated_data['name'] = validated_data['name'].strip()
        return super().update(instance, validated_data)


class AdminHabitSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    schedule_time = serializers.TimeField(source='reminder_time', required=False, allow_null=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'user_username', 'category', 'category_name',
            'activity_name', 'description', 'duration',
            'is_active', 'schedule_time', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AdminHabitTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = HabitTemplate
        fields = [
            'id', 'category', 'category_name',
            'activity_name', 'description', 'duration',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
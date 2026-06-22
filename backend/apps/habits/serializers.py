from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Category, Habit, HabitCompletion, HabitTemplate, HabitMaterial, TemplateCompletion, FREE_HABIT_LIMIT, DAILY_COMPLETION_LIMIT


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
    material_url = serializers.SerializerMethodField()
    material_type = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'category', 'category_detail',
            'activity_name', 'description', 'duration',
            'is_active', 'schedule_time', 'reminder_time', 'is_completed_today',
            'material_url', 'material_type',
            'created_at', 'updated_at', 'template_id',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_detail', 'is_completed_today', 'material_url', 'material_type']

    def _completion_user(self):
        return self.context.get('resolved_user') or self.context.get('request').user

    def get_is_completed_today(self, obj):
        user = self._completion_user()
        if not user or not getattr(user, 'is_authenticated', True):
            return False
        today = timezone.localdate()
        return HabitCompletion.objects.filter(
            user=user, habit=obj, completed_date=today
        ).exists()

    def get_material_url(self, obj):
        material = getattr(obj, 'material', None)
        if material is None:
            return None
        if material.material_type == 'video' and material.video_url:
            return material.video_url
        if material.file:
            request = self.context.get('request')
            file_url = material.file.url
            return request.build_absolute_uri(file_url) if request is not None else file_url
        return None

    def get_material_type(self, obj):
        material = getattr(obj, 'material', None)
        return material.material_type if material else None

    def create(self, validated_data):
        validated_data['user'] = self.context.get('resolved_user') or self.context['request'].user
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            msg = ' '.join(e.messages) if e.messages else str(e)
            raise serializers.ValidationError(msg)


class HabitSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    schedule_time = serializers.TimeField(source='reminder_time', read_only=True)
    is_completed_today = serializers.SerializerMethodField()
    material_url = serializers.SerializerMethodField()
    material_type = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'activity_name', 'description',
            'category_name', 'category_icon', 'duration', 'is_active', 'schedule_time',
            'is_completed_today', 'material_url', 'material_type', 'created_at',
        ]

    def _completion_user(self):
        return self.context.get('resolved_user') or self.context.get('request').user

    def get_is_completed_today(self, obj):
        user = self._completion_user()
        if not user or not getattr(user, 'is_authenticated', True):
            return False
        today = timezone.localdate()
        return HabitCompletion.objects.filter(
            user=user, habit=obj, completed_date=today
        ).exists()

    def get_material_url(self, obj):
        material = getattr(obj, 'material', None)
        if material is None:
            return None
        if material.material_type == 'video' and material.video_url:
            return material.video_url
        if material.file:
            request = self.context.get('request')
            file_url = material.file.url
            return request.build_absolute_uri(file_url) if request is not None else file_url
        return None

    def get_material_type(self, obj):
        material = getattr(obj, 'material', None)
        return material.material_type if material else None

    @staticmethod
    def from_template(template, user=None):
        """Same list shape as a user habit, using the template's numeric id."""
        today = timezone.localdate()
        is_completed = False
        if user and user.is_authenticated:
            is_completed = TemplateCompletion.objects.filter(
                user=user, template=template, completed_date=today
            ).exists()

        material = HabitMaterial.objects.filter(template=template).first()
        material_url = None
        material_type = None
        if material:
            material_type = material.material_type
            if material.material_type == 'video' and material.video_url:
                material_url = material.video_url
            elif material.file:
                material_url = material.file.url

        return {
            'id': template.id,
            'activity_name': template.activity_name,
            'description': template.description,
            'category_name': template.category.name if template.category else None,
            'category_icon': template.category.icon if template.category else '',
            'duration': template.duration,
            'is_active': template.is_active,
            'schedule_time': None,
            'is_completed_today': is_completed,
            'material_url': material_url,
            'material_type': material_type,
            'created_at': template.created_at,
        }


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


class TemplateCompletionSerializer(serializers.ModelSerializer):
    habit = serializers.IntegerField(source='template_id', read_only=True)
    habit_name = serializers.CharField(source='template.activity_name', read_only=True)
    category_name = serializers.CharField(source='template.category.name', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TemplateCompletion
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


class HabitMaterialSerializer(serializers.ModelSerializer):
    habit_title = serializers.SerializerMethodField()
    habit_user = serializers.SerializerMethodField()
    file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = HabitMaterial
        fields = [
            'id', 'habit', 'habit_title', 'habit_user', 'title', 'description',
            'material_type', 'file', 'video_url',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_habit_title(self, obj):
        if obj.habit:
            return obj.habit.activity_name
        if obj.template:
            return obj.template.activity_name
        return None

    def get_habit_user(self, obj):
        if obj.habit:
            return obj.habit.user.username
        return None


class AdminHabitMaterialSerializer(serializers.ModelSerializer):
    habit_title = serializers.SerializerMethodField()
    habit_user = serializers.SerializerMethodField()
    file = serializers.FileField(required=False, allow_null=True)
    habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.all(),
        required=False,
        allow_null=True,
    )
    habit_template = serializers.PrimaryKeyRelatedField(
        queryset=HabitTemplate.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = HabitMaterial
        fields = [
            'id', 'habit', 'habit_title', 'habit_user', 'habit_template',
            'title', 'description',
            'material_type', 'file', 'video_url',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_habit_title(self, obj):
        if obj.habit:
            return obj.habit.activity_name
        if obj.template:
            return obj.template.activity_name
        return None

    def get_habit_user(self, obj):
        if obj.habit:
            return obj.habit.user.username
        return None
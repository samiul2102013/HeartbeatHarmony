from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

FREE_HABIT_LIMIT = 3
DAILY_COMPLETION_LIMIT = 3

class Category(models.Model):
    """Admin-managed habit categories (e.g. Fitness, Mindfulness, Sleep)."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'habit_categories'
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='habits'
    )
    source_template = models.ForeignKey(
        'HabitTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adopted_habits',
        help_text='Admin template this habit was created from, if any.',
    )
    activity_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    is_active = models.BooleanField(default=True, db_index=True)
    reminder_time = models.TimeField(null=True, blank=True, help_text="Scheduled time to perform this habit (e.g., 08:00)")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habits'
        ordering = ['-created_at']

    def clean(self):
        # Enforce free tier limit (exclude self on updates)
        if not self.pk:
            from .utils import is_user_premium
            if not is_user_premium(self.user):
                existing = Habit.objects.filter(user=self.user, is_active=True).count()
                if existing >= FREE_HABIT_LIMIT:
                    raise ValidationError(
                        f"Free plan allows up to {FREE_HABIT_LIMIT} habits. Upgrade to Pro for unlimited habits."
                    )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.activity_name}"


class HabitTemplate(models.Model):
    """Admin-managed prebuilt habits under each category."""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='templates'
    )
    activity_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habit_templates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category.name} — {self.activity_name}"


class HabitMaterial(models.Model):
    class MaterialType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        VIDEO = 'video', 'Video Link'

    habit = models.OneToOneField(
        Habit,
        on_delete=models.CASCADE,
        related_name='material'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    material_type = models.CharField(
        max_length=10, choices=MaterialType.choices, default=MaterialType.PDF, db_index=True
    )
    file = models.FileField(
        upload_to='habits/materials/', null=True, blank=True,
        help_text='Upload material file (PDF or Video)'
    )
    video_url = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habit_materials'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.habit.activity_name} — {self.title}"


class HabitCompletion(models.Model):
    """Tracks when a premium user marks a habit as done for a given day."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habit_completions'
    )
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_date = models.DateField(help_text="Calendar date of completion")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'habit_completions'
        unique_together = ['user', 'habit', 'completed_date']
        ordering = ['-completed_date', '-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.habit.activity_name} — {self.completed_date}"
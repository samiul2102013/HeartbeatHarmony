from django.utils import timezone
from django.db import models as dm
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Habit, HabitTemplate


def is_user_premium(user):
    """Check if user has pro plan or an active (non-expired) InAppPurchase."""
    if getattr(user, 'plan', None) == 'pro':
        return True
    from apps.iap.models import InAppPurchase
    return InAppPurchase.objects.filter(
        user=user,
        is_verified=True,
    ).filter(
        dm.Q(expires_at__isnull=True) | dm.Q(expires_at__gt=timezone.now())
    ).exists()


def get_adopted_template_ids(user):
    return set(
        Habit.objects.filter(
            user=user,
            is_active=True,
            source_template_id__isnull=False,
        ).values_list('source_template_id', flat=True)
    )


def get_or_create_habit_from_template(user, template):
    """Return the user's habit for this template, creating it if needed."""
    habit = Habit.objects.filter(
        user=user,
        source_template=template,
        is_active=True,
    ).first()
    if habit:
        return habit, False

    habit = Habit.objects.create(
        user=user,
        category=template.category,
        activity_name=template.activity_name,
        description=template.description,
        duration=template.duration,
        source_template=template,
    )
    return habit, True


def resolve_user_habit(user, habit_or_template_pk):
    """
    Resolve a numeric id to a Habit for this user.
    If pk matches an adopted habit, return it.
    Otherwise return None (no materialization; callers handle templates separately).
    """
    habit = Habit.objects.filter(
        pk=habit_or_template_pk,
        user=user,
        is_active=True,
    ).first()
    if habit:
        return habit, None
    return None, 'Habit not found.'

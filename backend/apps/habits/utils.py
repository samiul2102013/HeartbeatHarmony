from django.utils import timezone
from django.db import models as dm

from .models import Habit, HabitTemplate


def is_user_premium(user):
    """Check if user has an active (non-expired) InAppPurchase."""
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
    If pk matches an active template, materialize and return it.
    """
    habit = Habit.objects.filter(
        pk=habit_or_template_pk,
        user=user,
        is_active=True,
    ).first()
    if habit:
        return habit, None

    template = HabitTemplate.objects.filter(
        pk=habit_or_template_pk,
        is_active=True,
    ).first()
    if not template:
        return None, 'Habit not found.'

    habit, _ = get_or_create_habit_from_template(user, template)
    return habit, None

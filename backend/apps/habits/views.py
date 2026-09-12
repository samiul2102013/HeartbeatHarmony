from django.db import models
from django.core.cache import caches
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Count, Prefetch, Case, When, Value, IntegerField, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Category, Habit, HabitCompletion, HabitMaterial, FREE_HABIT_LIMIT, DAILY_COMPLETION_LIMIT
from .utils import is_user_premium
from .serializers import (
    CategorySerializer, HabitSerializer, HabitSummarySerializer,
    HabitCompletionSerializer, HabitReminderSerializer,
    AdminCategorySerializer, AdminHabitSerializer,
    HabitMaterialSerializer, AdminHabitMaterialSerializer,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response, error_response


# ── User / Mobile Views ───────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    """Active categories for the habit creation form picker (shared payload — cached 5 min)."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        cache = caches['default']
        cached = cache.get('habit-categories:active')
        if cached is None:
            cached = CategorySerializer(self.get_queryset(), many=True).data
            cache.set('habit-categories:active', cached, 300)
        return Response({"data": cached})


class HabitListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    """Single unified feed over one `habits` table.

    Sort: 1. admin-created habits, 2. request.user's own habits,
    3. all other users' habits. Completions stay per-user via
    HabitCompletion(user=request.user, habit=...).
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HabitSerializer
        return HabitSummarySerializer

    def get_queryset(self):
        user = self.request.user
        today = timezone.localdate()
        return (
            Habit.objects.filter(is_active=True)
            .select_related('category', 'user')
            .prefetch_related(
                Prefetch('material', queryset=HabitMaterial.objects.all()),
                Prefetch(
                    'completions',
                    queryset=HabitCompletion.objects.filter(
                        user=user, completed_date=today
                    ).only('id', 'habit_id'),
                    to_attr='today_completions',
                ),
            )
            .annotate(
                section=Case(
                    When(Q(user__is_staff=True) | Q(user__role='admin'), then=Value(0)),
                    When(user=user, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by('section', '-created_at')
        )

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        all_habits = list(serializer.data)

        today = timezone.localdate()
        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        is_pro = is_user_premium(user)
        own_count = Habit.objects.filter(user=user, is_active=True).count()
        count = len(all_habits)
        return success_response(
            {
                'habits': all_habits,
                'count': count,
                'limit': FREE_HABIT_LIMIT,
                'is_pro': is_pro,
                'can_create': is_pro or own_count < FREE_HABIT_LIMIT,
                'daily_completions': completions_today,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'can_complete': is_pro or completions_today < DAILY_COMPLETION_LIMIT,
            },
            metadata={
                'current_page': 1,
                'per_page': count or 20,
                'total_items': count,
                'total_pages': 1,
                'has_next_page': False,
                'has_previous_page': False,
                'next_page': None,
                'previous_page': None,
            }
        )


class HabitMarkDoneView(StandardizedResponseMixin, APIView):
    """
    POST /habits/<pk>/done/
    Mark any visible habit done for today. Completion is per-user:
    HabitCompletion(user=request.user, habit=<pk>), so one user's done
    never flips another user's state. Habit stays visible with
    is_completed_today=true until the next day.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        today = timezone.localdate()

        habit = Habit.objects.filter(pk=pk, is_active=True).first()
        if not habit:
            return error_response('Habit not found.', status_code=status.HTTP_404_NOT_FOUND)
        if HabitCompletion.objects.filter(user=user, habit=habit, completed_date=today).exists():
            return error_response('This habit is already marked as done for today.')

        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        # Free user limits
        if not is_user_premium(user):
            if completions_today >= DAILY_COMPLETION_LIMIT:
                return error_response(
                    f'Daily limit reached. You can mark up to {DAILY_COMPLETION_LIMIT} habits as done per day.'
                )

        completion = HabitCompletion.objects.create(
            user=user, habit=habit, completed_date=today,
        )
        completion_data = HabitCompletionSerializer(completion).data

        return success_response(
            {
                'completion': completion_data,
                'daily_completions': completions_today + 1,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'remaining': DAILY_COMPLETION_LIMIT - (completions_today + 1),
            },
            message='Habit marked as done!',
            status_code=status.HTTP_201_CREATED,
        )


class HabitReminderTodayView(StandardizedResponseMixin, generics.ListAPIView):
    """
    GET /habits/reminders/today/
    Returns all active habits with reminder_time set for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HabitReminderSerializer
    pagination_class = None

    def get_queryset(self):
        return Habit.objects.filter(
            user=self.request.user,
            is_active=True,
            reminder_time__isnull=False
        ).select_related('category').order_by('reminder_time')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response({'reminders': serializer.data, 'count': len(serializer.data)})


# ── Admin Views ───────────────────────────────────────────────

class AdminCategoryListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return Category.objects.annotate(
            habit_count=Count('habits')
        ).order_by('name')


class AdminCategoryDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminCategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(habit_count=Count('habits'))

    def put(self, request, *args, **kwargs):
        # Allow the frontend to submit only changed fields on edit.
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class AdminHabitListView(StandardizedResponseMixin, generics.ListCreateAPIView):
    """Admin creates habits in the same `habits` table (user=admin)."""
    queryset = Habit.objects.select_related('user', 'category').order_by('-created_at')
    serializer_class = AdminHabitSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['user__username', 'activity_name']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdminHabitDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.select_related('user', 'category')
    serializer_class = AdminHabitSerializer
    permission_classes = [IsAdminRole]

    def put(self, request, *args, **kwargs):
        # Allow the frontend to submit only changed fields on edit.
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class HabitMaterialListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return AdminHabitMaterialSerializer
        return HabitMaterialSerializer

    def get_queryset(self):
        queryset = HabitMaterial.objects.select_related('habit', 'habit__user', 'template').annotate(
            is_admin_created=Case(
                When(template__isnull=False, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('is_admin_created', '-created_at')
        habit_id = self.request.query_params.get('habit')
        if habit_id:
            queryset = queryset.filter(habit_id=habit_id)
        user = self.request.user
        if not (user.is_staff or getattr(user, 'role', None) == 'admin'):
            queryset = queryset.filter(
                models.Q(habit__user=user) | models.Q(template__isnull=False)
            )
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        habit = serializer.validated_data.get('habit')
        habit_template = serializer.validated_data.pop('habit_template', None)

        if habit_template:
            material, _ = HabitMaterial.objects.update_or_create(
                template=habit_template,
                defaults=serializer.validated_data,
            )
            serializer.instance = material
            return

        if not habit:
            raise serializers.ValidationError(
                {'habit': 'A habit or habit_template must be provided.'}
            )

        if not (user.is_staff or getattr(user, 'role', None) == 'admin') and habit.user_id != user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only add materials to your own habits.')

        template_id = habit.source_template_id
        material, _ = HabitMaterial.objects.update_or_create(
            habit=habit,
            defaults={
                **serializer.validated_data,
                'template_id': template_id,
            },
        )
        serializer.instance = material


class HabitMaterialDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return AdminHabitMaterialSerializer
        return HabitMaterialSerializer

    def get_queryset(self):
        queryset = HabitMaterial.objects.select_related('habit', 'habit__user', 'template')
        user = self.request.user
        if not (user.is_staff or getattr(user, 'role', None) == 'admin'):
            queryset = queryset.filter(
                models.Q(habit__user=user) | models.Q(template__isnull=False)
            )
        return queryset


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='Material deleted successfully.', status_code=status.HTTP_200_OK)

class HabitMaterialEditView(HabitMaterialDetailView):
    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.partial_update(request, *args, **kwargs)


class HabitMaterialDeleteView(HabitMaterialDetailView):
    pass


# ── Habit template compatibility aliases ──────────────────────────────
# The legacy habit_templates table was merged into the unified `habits`
# table (user=admin rows act as the catalog). The admin dashboard still
# calls /api/admin/habit-templates/, so these views serve it from `habits`.

class AdminHabitTemplateListCreateView(AdminHabitListView):
    """List/create template habits from the unified habits table."""
    queryset = Habit.objects.select_related('user', 'category').filter(
        user__is_staff=True
    ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdminHabitTemplateDetailView(AdminHabitDetailView):
    """Retrieve/update/delete template habits from the unified habits table."""
    queryset = Habit.objects.select_related('user', 'category')

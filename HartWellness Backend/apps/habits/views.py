from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.contrib.auth import get_user_model

from .models import Category, Habit, HabitCompletion, HabitTemplate, FREE_HABIT_LIMIT, DAILY_COMPLETION_LIMIT
from .serializers import (
    CategorySerializer, HabitSerializer, HabitSummarySerializer,
    HabitCompletionSerializer,
    AdminCategorySerializer, AdminHabitSerializer,
    HabitTemplateSerializer, AdminHabitTemplateSerializer,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response, error_response


# ── Testing helper: bypass auth by falling back to first user ──

def _resolve_user(request):
    """Return authenticated user, or first DB user for unauthenticated testing."""
    if request.user.is_authenticated:
        return request.user
    user = get_user_model().objects.first()
    if not user:
        raise Exception('No users in database for testing.')
    return user


# ── User / Mobile Views ───────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    """Active categories for the habit creation form picker."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})


class HabitListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HabitSerializer
        return HabitSummarySerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['resolved_user'] = _resolve_user(self.request)
        return ctx

    def get_queryset(self):
        return Habit.objects.filter(
            user=_resolve_user(self.request), is_active=True
        ).select_related('category')

    def list(self, request, *args, **kwargs):
        user = _resolve_user(request)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        today = timezone.localdate()
        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        return success_response({
            'habits': serializer.data,
            'count': queryset.count(),
            'limit': FREE_HABIT_LIMIT,
            'is_pro': getattr(user, 'is_pro', False),
            'can_create': getattr(user, 'is_pro', False) or queryset.count() < FREE_HABIT_LIMIT,
            'daily_completions': completions_today,
            'daily_completion_limit': DAILY_COMPLETION_LIMIT,
            'can_complete': completions_today < DAILY_COMPLETION_LIMIT,
        })


class HabitDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['resolved_user'] = _resolve_user(self.request)
        return ctx

    def get_queryset(self):
        return Habit.objects.filter(user=_resolve_user(self.request))

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class HabitMarkDoneView(StandardizedResponseMixin, APIView):
    """
    POST /habits/<pk>/done/
    User marks a habit as done for today.
    Enforces the 3 completions/day limit across all categories.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        user = _resolve_user(request)

        # Validate habit belongs to user and is active
        try:
            habit = Habit.objects.get(pk=pk, user=user, is_active=True)
        except Habit.DoesNotExist:
            return error_response(
                'Habit not found.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.localdate()

        # Check if already marked done today
        if HabitCompletion.objects.filter(user=user, habit=habit, completed_date=today).exists():
            return error_response('This habit is already marked as done for today.')

        # Check daily limit across all categories
        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        if completions_today >= DAILY_COMPLETION_LIMIT:
            return error_response(
                f'Daily limit reached. You can mark up to {DAILY_COMPLETION_LIMIT} habits as done per day.'
            )

        # Create the completion
        completion = HabitCompletion.objects.create(
            user=user,
            habit=habit,
            completed_date=today,
        )

        return success_response(
            {
                'completion': HabitCompletionSerializer(completion).data,
                'daily_completions': completions_today + 1,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'remaining': DAILY_COMPLETION_LIMIT - (completions_today + 1),
            },
            message='Habit marked as done!',
            status_code=status.HTTP_201_CREATED,
        )


class HabitUndoView(StandardizedResponseMixin, APIView):
    """
    DELETE /habits/<pk>/undo/
    Undo today's completion for a habit.
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk):
        user = _resolve_user(request)
        today = timezone.localdate()
        deleted, _ = HabitCompletion.objects.filter(
            user=user, habit_id=pk, completed_date=today
        ).delete()

        if not deleted:
            return error_response(
                'No completion found for this habit today.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        return success_response(
            {
                'daily_completions': completions_today,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'remaining': DAILY_COMPLETION_LIMIT - completions_today,
            },
            message='Habit completion undone.',
        )


class DailyHabitStatusView(StandardizedResponseMixin, APIView):
    """
    GET /habits/daily-status/
    Returns today's completion summary for the authenticated user.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = _resolve_user(request)
        today = timezone.localdate()
        completions = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).select_related('habit', 'habit__category')

        return success_response({
            'date': str(today),
            'is_pro': getattr(user, 'is_pro', False),
            'completions': HabitCompletionSerializer(completions, many=True).data,
            'daily_completions': completions.count(),
            'daily_completion_limit': DAILY_COMPLETION_LIMIT,
            'remaining': max(0, DAILY_COMPLETION_LIMIT - completions.count()),
            'can_complete': completions.count() < DAILY_COMPLETION_LIMIT,
        })


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


class AdminHabitListView(StandardizedResponseMixin, generics.ListAPIView):
    queryset = Habit.objects.select_related('user', 'category').order_by('-created_at')
    serializer_class = AdminHabitSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['user__username', 'activity_name']


class AdminHabitTemplateListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    queryset = HabitTemplate.objects.select_related('category').order_by('-created_at')
    serializer_class = AdminHabitTemplateSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['activity_name', 'description', 'category__name']


class AdminHabitTemplateDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = HabitTemplate.objects.select_related('category')
    serializer_class = AdminHabitTemplateSerializer
    permission_classes = [IsAdminRole]

    def put(self, request, *args, **kwargs):
        # Allow partial updates from admin edit form.
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ── Habit Template Views ─────────────────────────────────────

class HabitTemplateListView(generics.ListAPIView):
    """User-facing list of active habit templates, filterable by category."""
    queryset = HabitTemplate.objects.filter(is_active=True)
    serializer_class = HabitTemplateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginator = self.paginator
            return Response({
                "success": True,
                "message": "Habit templates retrieved successfully",
                "status": 200,
                "data": serializer.data,
                "metadata": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "page": paginator.page.number,
                    "page_size": paginator.page.paginator.per_page,
                }
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Habit templates retrieved successfully",
            "status": 200,
            "data": serializer.data,
            "metadata": {
                "count": len(serializer.data),
                "next": None,
                "previous": None,
                "page": 1,
                "page_size": len(serializer.data) or 20,
            }
        })

        today = timezone.localdate()

        # Check if already marked done today
        if HabitCompletion.objects.filter(user=user, habit=habit, completed_date=today).exists():
            return error_response('This habit is already marked as done for today.')

        # Check daily limit across all categories
        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        if completions_today >= DAILY_COMPLETION_LIMIT:
            return error_response(
                f'Daily limit reached. You can mark up to {DAILY_COMPLETION_LIMIT} habits as done per day.'
            )

        # Create the completion
        completion = HabitCompletion.objects.create(
            user=user,
            habit=habit,
            completed_date=today,
        )

        return success_response(
            {
                'completion': HabitCompletionSerializer(completion).data,
                'daily_completions': completions_today + 1,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'remaining': DAILY_COMPLETION_LIMIT - (completions_today + 1),
            },
            message='Habit marked as done!',
            status_code=status.HTTP_201_CREATED,
        )


class HabitUndoView(StandardizedResponseMixin, APIView):
    """
    DELETE /habits/<pk>/undo/
    Undo today's completion for a habit.
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk):
        user = _resolve_user(request)
        today = timezone.localdate()
        deleted, _ = HabitCompletion.objects.filter(
            user=user, habit_id=pk, completed_date=today
        ).delete()

        if not deleted:
            return error_response(
                'No completion found for this habit today.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        completions_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()

        return success_response(
            {
                'daily_completions': completions_today,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'remaining': DAILY_COMPLETION_LIMIT - completions_today,
            },
            message='Habit completion undone.',
        )


# ... (rest of the code remains the same)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
from django.db import models
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Count, Prefetch, Case, When, Value, IntegerField, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Category, Habit, HabitCompletion, HabitTemplate, HabitMaterial, TemplateCompletion, FREE_HABIT_LIMIT, DAILY_COMPLETION_LIMIT
from .utils import is_user_premium
from .serializers import (
    CategorySerializer, HabitSerializer, HabitSummarySerializer,
    HabitCompletionSerializer, TemplateCompletionSerializer, HabitReminderSerializer,
    AdminCategorySerializer, AdminHabitSerializer,
    HabitTemplateSerializer, AdminHabitTemplateSerializer,
    HabitMaterialSerializer, AdminHabitMaterialSerializer,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response, error_response


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
        habit_comp_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()
        template_comp_today = TemplateCompletion.objects.filter(
            user=user, completed_date=today
        ).count()
        completions_today = habit_comp_today + template_comp_today

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


class HabitDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
class HabitDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """Read any visible habit; write only own habit or admin."""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_active=True).select_related(
            'category', 'user'
        ).prefetch_related(
            Prefetch('material', queryset=HabitMaterial.objects.all()),
        )

    def _check_write(self, obj):
        user = self.request.user
        is_admin = user.is_staff or getattr(user, 'role', None) == 'admin'
        if obj.user_id != user.id and not is_admin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only modify your own habits.')

    def perform_update(self, serializer):
        self._check_write(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        self._check_write(instance)
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=['is_active'])


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
        if habit:
            if HabitCompletion.objects.filter(user=user, habit=habit, completed_date=today).exists():
                return error_response('This habit is already marked as done for today.')
        else:
            # Backward compat: old clients may still send a template id
            # (template and habit ids used to share one list).
            template = HabitTemplate.objects.filter(pk=pk, is_active=True).first()
            if template:
                if TemplateCompletion.objects.filter(user=user, template=template, completed_date=today).exists():
                    return error_response('This habit is already marked as done for today.')
            else:
                return error_response('Habit not found.', status_code=status.HTTP_404_NOT_FOUND)

        habit_comp_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()
        template_comp_today = TemplateCompletion.objects.filter(
            user=user, completed_date=today
        ).count()
        completions_today = habit_comp_today + template_comp_today

        # Free user limits
        if not is_user_premium(user):
            if completions_today >= DAILY_COMPLETION_LIMIT:
                return error_response(
                    f'Daily limit reached. You can mark up to {DAILY_COMPLETION_LIMIT} habits as done per day.'
                )

        if habit:
            completion = HabitCompletion.objects.create(
                user=user, habit=habit, completed_date=today,
            )
            completion_data = HabitCompletionSerializer(completion).data
        else:
            template = HabitTemplate.objects.get(pk=pk)
            tc = TemplateCompletion.objects.create(
                user=user, template=template, completed_date=today,
            )
            completion_data = TemplateCompletionSerializer(tc).data

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


class HabitUndoView(StandardizedResponseMixin, APIView):
    """
    DELETE /habits/<pk>/undo/
    Undo request.user's own completion for today on any visible habit.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        user = request.user
        today = timezone.localdate()

        habit = Habit.objects.filter(pk=pk, is_active=True).first()
        if habit:
            deleted, _ = HabitCompletion.objects.filter(
                user=user, habit=habit, completed_date=today
            ).delete()
        else:
            template = HabitTemplate.objects.filter(pk=pk, is_active=True).first()
            if not template:
                return error_response('Habit not found.', status_code=status.HTTP_404_NOT_FOUND)
            deleted, _ = TemplateCompletion.objects.filter(
                user=user, template=template, completed_date=today
            ).delete()

        if not deleted:
            return error_response(
                'No completion found for this habit today.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        habit_comp_today = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).count()
        template_comp_today = TemplateCompletion.objects.filter(
            user=user, completed_date=today
        ).count()
        completions_today = habit_comp_today + template_comp_today

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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        habit_completions = HabitCompletion.objects.filter(
            user=user, completed_date=today
        ).select_related('habit', 'habit__category')
        template_completions = TemplateCompletion.objects.filter(
            user=user, completed_date=today
        ).select_related('template', 'template__category')

        is_pro = is_user_premium(user)
        comp_count = habit_completions.count() + template_completions.count()
        return success_response(
            {
                'completions': HabitCompletionSerializer(habit_completions, many=True).data,
                'date': str(today),
                'is_pro': is_pro,
                'daily_completions': comp_count,
                'daily_completion_limit': DAILY_COMPLETION_LIMIT,
                'remaining': max(0, DAILY_COMPLETION_LIMIT - comp_count),
                'can_complete': is_pro or comp_count < DAILY_COMPLETION_LIMIT,
            },
            metadata={
                'current_page': 1,
                'per_page': comp_count or 20,
                'total_items': comp_count,
                'total_pages': 1,
                'has_next_page': False,
                'has_previous_page': False,
                'next_page': None,
                'previous_page': None,
            }
        )


class HabitReminderListView(StandardizedResponseMixin, generics.ListAPIView):
    """
    GET /habits/reminders/
    Returns all active habits for the user that have a reminder_time set, ordered by time.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HabitSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(
            user=user,
            is_active=True,
            reminder_time__isnull=False
        ).order_by('reminder_time')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        count = queryset.count()
        
        return success_response(
            {
                'reminders': serializer.data,
                'count': count
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


class HabitMaterialByHabitView(StandardizedResponseMixin, APIView):
    """
    GET /api/habits/<pk>/material/
    Returns the material attached to a habit or template, or 404 if none exists.
    Owners and admins can read; non-owners get 404 (not 403) to avoid leaking
    that the habit exists.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        is_admin = user.is_staff or getattr(user, 'role', None) == 'admin'

        # Try to find by habit first
        try:
            habit = Habit.objects.select_related('user', 'category').get(pk=pk)
        except Habit.DoesNotExist:
            habit = None

        material = None
        if habit:
            if not is_admin and habit.user_id != user.id:
                return error_response('Habit not found.', status_code=status.HTTP_404_NOT_FOUND)
            material = HabitMaterial.objects.filter(habit=habit).first()

        # If no habit material, try template
        if material is None:
            template = HabitTemplate.objects.filter(pk=pk, is_active=True).first()
            if template:
                material = HabitMaterial.objects.filter(template=template).first()

        if material is None:
            return error_response(
                'No material attached to this habit.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer_class = (
            AdminHabitMaterialSerializer
            if is_admin else HabitMaterialSerializer
        )
        return success_response(serializer_class(material, context={'request': request}).data)


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
            current_page = paginator.page.number
            total_pages = paginator.page.paginator.num_pages
            per_page = paginator.page.paginator.per_page
            total_items = paginator.page.paginator.count
            return Response({
                "success": True,
                "message": "Habit templates retrieved successfully",
                "status": 200,
                "data": serializer.data,
                "metadata": {
                    "current_page": current_page,
                    "per_page": per_page,
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "has_next_page": current_page < total_pages,
                    "has_previous_page": current_page > 1,
                    "next_page": current_page + 1 if current_page < total_pages else None,
                    "previous_page": current_page - 1 if current_page > 1 else None,
                }
            })
        serializer = self.get_serializer(queryset, many=True)
        count = len(serializer.data)
        return Response({
            "success": True,
            "message": "Habit templates retrieved successfully",
            "status": 200,
            "data": serializer.data,
            "metadata": {
                "current_page": 1,
                "per_page": count or 20,
                "total_items": count,
                "total_pages": 1,
                "has_next_page": False,
                "has_previous_page": False,
                "next_page": None,
                "previous_page": None,
            }
        })
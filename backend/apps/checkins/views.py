from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Mood, CheckIn
from .serializers import (
    MoodSerializer, CheckInSerializer, CheckInSummarySerializer,
    AdminMoodSerializer, AdminCheckInSerializer,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response
from apps.core.image_utils import resize_image
from django.utils import timezone
import datetime
from apps.accounts.models import User


# ── Public/User Views ─────────────────────────────────────────

class MoodListView(StandardizedResponseMixin, generics.ListAPIView):
    """Active moods for the mobile picker."""
    queryset = Mood.objects.filter(is_active=True)
    serializer_class = MoodSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckInCreateView(StandardizedResponseMixin, generics.CreateAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckInHistoryView(StandardizedResponseMixin, generics.ListAPIView):
    """User's own check-in history with optional period filter."""
    serializer_class = CheckInSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = CheckIn.objects.filter(user=self.request.user)
        period = self.request.query_params.get('period')  # weekly / monthly / yearly
        if period == 'weekly':
            qs = qs.filter(created_at__week=self._current_week())
        elif period == 'monthly':
            qs = qs.filter(created_at__month=self._current_month(),
                           created_at__year=self._current_year())
        elif period == 'yearly':
            qs = qs.filter(created_at__year=self._current_year())
        return qs

    def _current_week(self):
        from django.utils import timezone
        return timezone.now().isocalendar()[1]

    def _current_month(self):
        from django.utils import timezone
        return timezone.now().month

    def _current_year(self):
        from django.utils import timezone
        return timezone.now().year


class CheckInDetailView(StandardizedResponseMixin, generics.RetrieveAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CheckIn.objects.filter(user=self.request.user)


class DashboardStatsView(StandardizedResponseMixin, APIView):
    """
    Returns aggregated scores for the home dashboard:
    - Latest check-in scores
    - 7-day average heart balance trend
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        latest = CheckIn.objects.filter(user=user).first()
        averages = CheckIn.objects.filter(user=user).aggregate(
            avg_mental=Avg('mental_clarity'),
            avg_emotional=Avg('emotional_balance'),
            avg_spiritual=Avg('spiritual_wellness'),
            avg_physical=Avg('physical_energy'),
            avg_heart_balance=Avg('heart_balance_score'),
            total_checkins=Count('id'),
        )

        # Last 7 daily averages for the trend chart
        seven_days_ago = timezone.now() - datetime.timedelta(days=7)
        trend = (
            CheckIn.objects
            .filter(user=user, created_at__gte=seven_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(avg_score=Avg('heart_balance_score'))
            .order_by('date')
        )

        return success_response({
            'latest': CheckInSerializer(latest).data if latest else None,
            'averages': averages,
            'trend': list(trend),
        })


class MyProgressView(StandardizedResponseMixin, APIView):
    """User progress over the last 7 days grouped by weekday."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        start_date = today - datetime.timedelta(days=6)

        checkins = (
            CheckIn.objects
            .filter(user=request.user, created_at__date__range=(start_date, today))
            .select_related('mood')
            .order_by('created_at')
        )

        grouped_checkins = {
            start_date + datetime.timedelta(days=index): []
            for index in range(7)
        }
        for checkin in checkins:
            grouped_checkins.setdefault(checkin.created_at.date(), []).append(checkin)

        days = []
        for index in range(7):
            current_date = start_date + datetime.timedelta(days=index)
            day_checkins = grouped_checkins.get(current_date, [])
            average_score = None
            if day_checkins:
                average_score = round(
                    sum(float(item.heart_balance_score) for item in day_checkins) / len(day_checkins),
                    2,
                )

            days.append({
                'date': current_date,
                'day_name': current_date.strftime('%A'),
                'total_checkins': len(day_checkins),
                'average_heart_balance': average_score,
                'checkins': CheckInSummarySerializer(day_checkins, many=True).data,
            })

        summary = checkins.aggregate(avg_heart_balance=Avg('heart_balance_score'))

        return success_response({
            'range_start': start_date,
            'range_end': today,
            'total_checkins': checkins.count(),
            'average_heart_balance': summary.get('avg_heart_balance'),
            'days': days,
        })


# ── Admin Views ───────────────────────────────────────────────

class AdminMoodListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    queryset = Mood.objects.all().order_by('name')
    serializer_class = AdminMoodSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        data = self._resize_svg(serializer.validated_data)
        serializer.save(**data)

    def _resize_svg(self, data):
        svg = data.get('svg')
        if svg and hasattr(svg, 'read'):
            processed = resize_image(svg, max_size=300, quality=85)
            if processed:
                data['svg'] = processed
        return data


class AdminMoodDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Mood.objects.all()
    serializer_class = AdminMoodSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_update(self, serializer):
        svg = serializer.validated_data.get('svg')
        if svg and hasattr(svg, 'read'):
            processed = resize_image(svg, max_size=300, quality=85)
            if processed:
                serializer.validated_data['svg'] = processed
        serializer.save()


class AdminCheckInListView(StandardizedResponseMixin, generics.ListAPIView):
    queryset = CheckIn.objects.select_related('user', 'mood').order_by('-created_at')
    serializer_class = AdminCheckInSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['user', 'mood']
    ordering_fields = ['created_at', 'heart_balance_score']
    search_fields = ['user__username', 'user__email', 'mood__name']


class AdminCheckInDetailView(StandardizedResponseMixin, generics.RetrieveDestroyAPIView):
    queryset = CheckIn.objects.all()
    serializer_class = AdminCheckInSerializer
    permission_classes = [IsAdminRole]


class AdminDashboardView(StandardizedResponseMixin, APIView):
    """
    Admin dashboard stats:
    - Heart balance trend across ALL users
    - Mood distribution across ALL users
    - User insights (total, active, pro)
    """
    permission_classes = [IsAdminRole]

    def get(self, request):

        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)

        trend = (
            CheckIn.objects
            .filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(avg_score=Avg('heart_balance_score'))
            .order_by('date')
        )

        mood_distribution = (
            CheckIn.objects
            .filter(created_at__gte=thirty_days_ago)
            .values('mood__name', 'mood__emoji')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        user_insights = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(is_active=True)),
            pro=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(plan='pro')),
        )

        return success_response({
            'heart_balance_trend': list(trend),
            'mood_distribution': list(mood_distribution),
            'user_insights': user_insights,
        })
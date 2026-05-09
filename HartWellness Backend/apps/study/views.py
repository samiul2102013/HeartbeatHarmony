from django.utils import timezone
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import (
    StudyTopic, StudyMaterial, UserMaterialProgress,
    Quiz, Question, QuizAttempt, QuizAnswer
)
from .serializers import (
    StudyTopicListSerializer, StudyTopicSerializer,
    StudyMaterialListSerializer, StudyMaterialSerializer, StudyMaterialCatalogSerializer,
    MarkMaterialCompleteSerializer,
    QuizListSerializer, QuizSerializer,
    QuizSubmitSerializer, QuizAttemptSerializer, QuizAttemptDetailSerializer,
    TopicQuizHistorySerializer,
    AdminStudyTopicSerializer, AdminStudyMaterialSerializer,
    AdminQuizSerializer, AdminQuestionSerializer, AdminQuizAttemptSerializer,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response, error_response


# ── User / Mobile — Study Topics ─────────────────────────────

class StudyTopicListView(StandardizedResponseMixin, generics.ListAPIView):
    """Study page — list of topics with progress counts."""
    serializer_class = StudyTopicListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return StudyTopic.objects.filter(is_active=True).annotate(
            material_count=Count('materials', filter=__import__('django.db.models', fromlist=['Q']).Q(materials__is_active=True))
        )


class StudyTopicDetailView(StandardizedResponseMixin, generics.RetrieveAPIView):
    """Topic detail — includes all materials with completion status."""
    serializer_class = StudyTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Q
        return StudyTopic.objects.filter(is_active=True).annotate(
            material_count=Count('materials', filter=Q(materials__is_active=True))
        )


# ── User / Mobile — Study Materials ──────────────────────────

class StudyMaterialListView(StandardizedResponseMixin, generics.ListAPIView):
    """All active study materials with normalized fields for client apps."""
    serializer_class = StudyMaterialCatalogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return StudyMaterial.objects.filter(is_active=True).select_related('topic').order_by('-created_at')


class StudyMaterialDetailView(StandardizedResponseMixin, generics.RetrieveAPIView):
    """Material detail page — full content for reading."""
    serializer_class = StudyMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyMaterial.objects.filter(is_active=True)


class MarkMaterialCompleteView(StandardizedResponseMixin, APIView):
    """User marks a material as read/downloaded."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MarkMaterialCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        material_id = serializer.validated_data['material_id']
        try:
            material = StudyMaterial.objects.get(id=material_id, is_active=True)
        except StudyMaterial.DoesNotExist:
            return error_response(
                'Material not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

        progress, created = UserMaterialProgress.objects.get_or_create(
            user=request.user, material=material
        )
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save(update_fields=['is_completed', 'completed_at'])

        return success_response({'detail': 'Material marked as complete.', 'created': created})


# ── User / Mobile — Quiz ──────────────────────────────────────

class QuizListView(StandardizedResponseMixin, generics.ListAPIView):
    """Quiz section — list of quizzes with last score."""
    serializer_class = QuizListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Quiz.objects.filter(is_active=True).annotate(
            question_count=Count('questions')
        )


class QuizDetailView(StandardizedResponseMixin, generics.RetrieveAPIView):
    """Quiz questions page — returns questions WITHOUT correct answers."""
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(is_active=True).annotate(
            question_count=Count('questions')
        )


class QuizSubmitView(StandardizedResponseMixin, APIView):
    """
    User submits all answers at once.
    Returns score + per-answer results (quiz complete page).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quiz_id = serializer.validated_data['quiz_id']
        answers_data = serializer.validated_data['answers']

        try:
            quiz = Quiz.objects.get(id=quiz_id, is_active=True)
        except Quiz.DoesNotExist:
            return error_response(
                'Quiz not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

        questions = {q.id: q for q in quiz.questions.all()}
        score = 0
        answer_results = []

        # Create attempt first
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            total_questions=len(questions),
        )

        for answer in answers_data:
            question = questions.get(answer['question_id'])
            if not question:
                continue

            is_correct = answer['selected_option'] == question.correct_option
            if is_correct:
                score += 1

            QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=answer['selected_option'],
                is_correct=is_correct,
            )

            answer_results.append({
                'question_id': question.id,
                'question_text': question.text,
                'selected_option': answer['selected_option'],
                'correct_option': question.correct_option,
                'is_correct': is_correct,
            })

        attempt.score = score
        attempt.save(update_fields=['score'])

        return success_response({
            'attempt_id': attempt.id,
            'quiz_title': quiz.title,
            'score': score,
            'total_questions': attempt.total_questions,
            'score_percentage': attempt.score_percentage,
            'answers': answer_results,
        })


class MyQuizAttemptsView(StandardizedResponseMixin, generics.ListAPIView):
    """User's quiz history. Supports ?topic=<id> filter."""
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = QuizAttempt.objects.filter(
            user=self.request.user
        ).select_related('quiz', 'quiz__topic')

        topic_id = self.request.query_params.get('topic')
        if topic_id:
            qs = qs.filter(quiz__topic_id=topic_id)

        return qs


class QuizAttemptDetailView(StandardizedResponseMixin, generics.RetrieveAPIView):
    """Full attempt detail — for reviewing answers."""
    serializer_class = QuizAttemptDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)


class MyQuizAttemptsByTopicView(StandardizedResponseMixin, generics.ListAPIView):
    """
    GET /study/attempts/by-topic/
    Returns quiz history grouped by topic for the authenticated user.
    Only includes topics where the user has at least one attempt.
    """
    serializer_class = TopicQuizHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # Only return topics where this user has quiz attempts
        attempted_topic_ids = QuizAttempt.objects.filter(
            user=self.request.user
        ).values_list('quiz__topic_id', flat=True).distinct()

        return StudyTopic.objects.filter(
            id__in=attempted_topic_ids
        ).order_by('title')


class StudyProgressView(StandardizedResponseMixin, APIView):
    """
    Profile page — study progress summary.
    Total study hours, topics completed, quiz scores.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        materials_completed = UserMaterialProgress.objects.filter(
            user=user, is_completed=True
        ).count()

        total_materials = StudyMaterial.objects.filter(is_active=True).count()

        quiz_attempts = QuizAttempt.objects.filter(user=user)
        total_attempts = quiz_attempts.count()
        avg_score = 0
        if total_attempts:
            total_pct = sum(a.score_percentage for a in quiz_attempts)
            avg_score = round(total_pct / total_attempts, 1)

        return success_response({
            'materials_completed': materials_completed,
            'total_materials': total_materials,
            'completion_percentage': round(
                (materials_completed / total_materials * 100) if total_materials else 0, 1
            ),
            'total_quiz_attempts': total_attempts,
            'average_quiz_score_percentage': avg_score,
        })


# ── Admin Views ───────────────────────────────────────────────

class AdminStudyTopicListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    serializer_class = AdminStudyTopicSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return StudyTopic.objects.annotate(material_count=Count('materials'))


class AdminStudyTopicDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminStudyTopicSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return StudyTopic.objects.annotate(material_count=Count('materials'))


class AdminStudyMaterialListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    serializer_class = AdminStudyMaterialSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['topic', 'material_type', 'is_active']
    search_fields = ['title']

    def get_queryset(self):
        return StudyMaterial.objects.select_related('topic').order_by('-created_at')


class AdminStudyMaterialDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = StudyMaterial.objects.all()
    serializer_class = AdminStudyMaterialSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class AdminQuizListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    serializer_class = AdminQuizSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['topic', 'is_active']
    search_fields = ['title']

    def get_queryset(self):
        return Quiz.objects.annotate(question_count=Count('questions')).order_by('-created_at')


class AdminQuizDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminQuizSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Quiz.objects.annotate(question_count=Count('questions'))


class AdminQuestionListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    serializer_class = AdminQuestionSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']

    def get_queryset(self):
        return Question.objects.select_related('quiz').order_by('quiz', 'order')


class AdminQuestionDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = AdminQuestionSerializer
    permission_classes = [IsAdminRole]


class AdminQuizAttemptListView(StandardizedResponseMixin, generics.ListAPIView):
    """Admin — see all quiz results by user."""
    queryset = QuizAttempt.objects.select_related('user', 'quiz').order_by('-completed_at')
    serializer_class = AdminQuizAttemptSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['quiz', 'user']
    search_fields = ['user__username', 'quiz__title']
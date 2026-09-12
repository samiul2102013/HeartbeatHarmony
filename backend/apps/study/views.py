from django.db import transaction
from django.core.cache import caches
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import (
    StudyTopic, StudyMaterial,
    Quiz, Question, QuizAttempt, QuizAnswer
)
from .serializers import (
    StudyTopicListSerializer,
    StudyMaterialCatalogSerializer,
    QuizListSerializer, QuizSerializer,
    QuizSubmitSerializer,
    AdminStudyTopicSerializer, AdminStudyMaterialSerializer,
    AdminQuizSerializer, AdminQuizListSerializer, AdminQuestionSerializer, AdminQuizAttemptSerializer,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response, error_response


# ── User / Mobile — Study Topics ─────────────────────────────

class StudyTopicListView(StandardizedResponseMixin, generics.ListAPIView):
    """Study page — list of topics with progress counts (per-user payload, cached 5 min)."""
    serializer_class = StudyTopicListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return StudyTopic.objects.filter(is_active=True).annotate(
            material_count=Count('materials', filter=__import__('django.db.models', fromlist=['Q']).Q(materials__is_active=True)),
            question_count=Count('questions')
        )

    def list(self, request, *args, **kwargs):
        cache = caches['default']
        key = f'study-topics:user:{request.user.id}'
        cached = cache.get(key)
        if cached is None:
            cached = self.get_serializer(self.get_queryset(), many=True).data
            cache.set(key, cached, 300)
        return success_response(cached)


# ── User / Mobile — Study Materials ──────────────────────────

class StudyMaterialListView(StandardizedResponseMixin, generics.ListAPIView):
    """All active study materials with normalized fields for client apps."""
    serializer_class = StudyMaterialCatalogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return StudyMaterial.objects.filter(is_active=True).select_related('topic').order_by('-created_at')


# ── User / Mobile — Quiz ──────────────────────────────────────

class QuizListView(StandardizedResponseMixin, generics.ListAPIView):
    """Quiz section — list of quizzes with last score."""
    serializer_class = QuizListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # Evaluate the selected set in one query; fall back to the latest
        # quiz only when nothing is selected (avoids exists() + re-query).
        selected = list(
            Quiz.objects.filter(is_active=True, is_selected=True).annotate(
                question_count=Count('questions')
            )
        )
        if selected:
            return selected
        return Quiz.objects.filter(is_active=True).order_by('-created_at').annotate(
            question_count=Count('questions')
        )[:1]


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

        quiz_questions = list(quiz.questions.select_related('topic').all())
        questions = {q.id: q for q in quiz_questions}
        topic_question_totals = {}
        topic_lookup = {}

        for question in quiz_questions:
            if not question.topic_id:
                continue
            topic_question_totals[question.topic_id] = topic_question_totals.get(question.topic_id, 0) + 1
            topic_lookup[question.topic_id] = question.topic

        overall_score = 0
        answer_results = []
        topic_scores = {topic_id: 0 for topic_id in topic_question_totals}

        with transaction.atomic():
            overall_attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                total_questions=len(quiz_questions),
            )

            topic_attempts = {
                topic_id: QuizAttempt.objects.create(
                    user=request.user,
                    topic=topic_lookup[topic_id],
                    total_questions=topic_question_totals[topic_id],
                )
                for topic_id in topic_question_totals
            }

            for answer in answers_data:
                question = questions.get(answer['question_id'])
                if not question:
                    continue

                is_correct = answer['selected_option'] == question.correct_option
                if is_correct:
                    overall_score += 1

                QuizAnswer.objects.create(
                    attempt=overall_attempt,
                    question=question,
                    selected_option=answer['selected_option'],
                    is_correct=is_correct,
                )

                topic_attempt = topic_attempts.get(question.topic_id)
                if topic_attempt:
                    QuizAnswer.objects.create(
                        attempt=topic_attempt,
                        question=question,
                        selected_option=answer['selected_option'],
                        is_correct=is_correct,
                    )
                    if is_correct:
                        topic_scores[question.topic_id] += 1

                answer_results.append({
                    'question_id': question.id,
                    'question_text': question.text,
                    'topic_id': question.topic_id,
                    'topic_title': question.topic.title if question.topic else None,
                    'selected_option': answer['selected_option'],
                    'correct_option': question.correct_option,
                    'is_correct': is_correct,
                })

            overall_attempt.score = overall_score
            overall_attempt.save(update_fields=['score'])

            topic_results = []
            for topic_id, topic_attempt in topic_attempts.items():
                topic_attempt.score = topic_scores.get(topic_id, 0)
                topic_attempt.save(update_fields=['score'])
                topic_results.append({
                    'topic_id': topic_id,
                    'topic_title': topic_lookup[topic_id].title,
                    'attempt_id': topic_attempt.id,
                    'score': topic_attempt.score,
                    'total_questions': topic_attempt.total_questions,
                    'score_percentage': topic_attempt.score_percentage,
                })

        # Scores changed — invalidate this user's cached topic list.
        caches['default'].delete(f'study-topics:user:{request.user.id}')

        return success_response({
            'attempt_id': overall_attempt.id,
            'quiz_title': quiz.title,
            'score': overall_score,
            'total_questions': overall_attempt.total_questions,
            'score_percentage': overall_attempt.score_percentage,
            'topic_results': topic_results,
            'answers': answer_results,
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

    def perform_create(self, serializer):
        material = serializer.save()
        material_id = material.id
        material_title = material.title
        actor_id = self.request.user.id

        def _fanout():
            # Runs off-request so the upload response returns immediately.
            # Only plain values cross the thread boundary — never ORM objects.
            try:
                from apps.study.models import StudyMaterial
                from apps.study.video_utils import moov_at_front, run_faststart
                mat = StudyMaterial.objects.filter(id=material_id).first()
                if mat is not None and mat.pdf and mat.material_type == 'video':
                    src = mat.pdf.path
                    # NOTE: local-disk only. If USE_S3 is ever enabled, download
                    # to temp, process, and re-upload here instead of in-place replace.
                    if src.lower().endswith('.mp4') and not moov_at_front(src):
                        run_faststart(src, src)
            except Exception:
                import logging
                logging.getLogger(__name__).exception('video faststart failed')
            try:
                from apps.accounts.models import User
                from apps.notifications.models import Notification
                from apps.community.socketio_server import broadcast_event_sync

                users = User.objects.exclude(id=actor_id).filter(is_active=True)
                title = "New Study Material"
                message = f"A new study material has been uploaded: {material_title}."

                notifications = [
                    Notification(
                        user=user,
                        title=title,
                        message=message,
                        notification_type='study'
                    ) for user in users
                ]
                Notification.objects.bulk_create(notifications)

                from apps.community.socketio_server import COMMUNITY_GROUP
                broadcast_event_sync(COMMUNITY_GROUP, 'notification', {
                    'title': title,
                    'message': message,
                    'text': message,
                    'notification_type': 'study'
                })
            except Exception:
                import logging
                logging.getLogger(__name__).exception("study material fan-out failed")

        import threading
        threading.Thread(target=_fanout, daemon=True).start()


class AdminStudyMaterialDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = StudyMaterial.objects.all()
    serializer_class = AdminStudyMaterialSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class AdminQuizListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['topic', 'is_active']
    search_fields = ['title']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminQuizSerializer
        return AdminQuizListSerializer

    def get_queryset(self):
        return Quiz.objects.select_related('topic').prefetch_related('questions').annotate(question_count=Count('questions')).order_by('-created_at')

    def perform_create(self, serializer):
        quiz = serializer.save()
        
        from apps.accounts.models import User
        from apps.notifications.models import Notification
        from apps.community.socketio_server import broadcast_event_sync
        
        users = User.objects.exclude(id=self.request.user.id).filter(is_active=True)
        title = "New Quiz Available"
        message = f"A new quiz is ready for you: {quiz.title}. Test your knowledge!"
        
        notifications = [
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type='study'
            ) for user in users
        ]
        Notification.objects.bulk_create(notifications)

        from apps.community.socketio_server import COMMUNITY_GROUP
        broadcast_event_sync(COMMUNITY_GROUP, 'notification', {
            'title': title,
            'message': message,
            'text': message,
            'notification_type': 'study'
        })


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
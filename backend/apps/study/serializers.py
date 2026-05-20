from rest_framework import serializers
from .models import (
    StudyTopic, StudyMaterial, UserMaterialProgress,
    Quiz, Question, QuizAttempt, QuizAnswer
)


# ── Study Material Serializers ────────────────────────────────

class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'topic', 'title', 'description',
            'material_type', 'file', 'pdf', 'video_url', 'content',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StudyMaterialListSerializer(serializers.ModelSerializer):
    """Lightweight — for list views, excludes heavy content field."""
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'title', 'description', 'material_type',
            'file', 'pdf', 'video_url', 'is_completed', 'created_at',
        ]

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserMaterialProgress.objects.filter(
            user=request.user, material=obj, is_completed=True
        ).exists()


class TopicAttemptStatsMixin:
    def _get_user_attempts(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return QuizAttempt.objects.none()
        return QuizAttempt.objects.filter(
            user=request.user,
            topic=obj,
        ).order_by('-completed_at')

    def _get_last_attempt(self, obj):
        attempts = self._get_user_attempts(obj)
        last_attempt = attempts.first()
        if not last_attempt:
            return None
        return last_attempt

    def get_last_correct_answers(self, obj):
        last_attempt = self._get_last_attempt(obj)
        return last_attempt.score if last_attempt else 0

    def get_last_total_questions(self, obj):
        last_attempt = self._get_last_attempt(obj)
        return last_attempt.total_questions if last_attempt else 0

    def get_last_attempted_score(self, obj):
        last_attempt = self._get_last_attempt(obj)
        return last_attempt.score_percentage if last_attempt else 0

    def get_quiz_stats(self, obj):
        """Return last attempt + cumulative quiz stats for this user in this topic."""
        attempts = self._get_user_attempts(obj)
        if not attempts.exists():
            return None
        last = attempts.first()
        total_correct = sum(a.score for a in attempts)
        total_questions = sum(a.total_questions for a in attempts)
        return {
            'last_topic_title': last.topic.title if last.topic else None,
            'last_correct_answers': last.score,
            'last_total_questions': last.total_questions,
            'last_score_fraction': f"{last.score}/{last.total_questions}",
            'last_score_percentage': last.score_percentage,
            'total_correct_answers': total_correct,
            'total_questions_attempted': total_questions,
            'total_score_fraction': f"{total_correct}/{total_questions}",
        }


class StudyMaterialCatalogSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='title', read_only=True)
    topic = serializers.CharField(source='topic.title', read_only=True)
    subject = serializers.CharField(source='topic.title', read_only=True)
    type = serializers.CharField(source='material_type', read_only=True)
    material_data = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            'id',
            'material_name',
            'topic',
            'subject',
            'type',
            'material_data',
            'size',
            'description',
            'is_completed',
            'created_at',
            'updated_at',
        ]

    def _get_primary_file(self, obj):
        if obj.pdf:
            return obj.pdf
        if obj.file:
            return obj.file
        return None

    def get_material_data(self, obj):
        request = self.context.get('request')
        if obj.material_type == StudyMaterial.MaterialType.VIDEO and obj.video_url:
            return obj.video_url

        material_file = self._get_primary_file(obj)
        if material_file and getattr(material_file, 'url', None):
            if request:
                return request.build_absolute_uri(material_file.url)
            return material_file.url

        return None

    def get_size(self, obj):
        material_file = self._get_primary_file(obj)
        if not material_file:
            return None
        try:
            return material_file.size
        except Exception:
            return None

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserMaterialProgress.objects.filter(
            user=request.user, material=obj, is_completed=True
        ).exists()


class StudyTopicSerializer(TopicAttemptStatsMixin, serializers.ModelSerializer):
    materials = StudyMaterialListSerializer(many=True, read_only=True)
    material_count = serializers.IntegerField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.SerializerMethodField()
    last_correct_answers = serializers.SerializerMethodField()
    last_total_questions = serializers.SerializerMethodField()
    last_attempted_score = serializers.SerializerMethodField()

    class Meta:
        model = StudyTopic
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'material_count', 'question_count', 'completed_count', 'last_correct_answers', 'last_total_questions', 'last_attempted_score', 'materials', 'created_at',
        ]

    def get_completed_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserMaterialProgress.objects.filter(
            user=request.user,
            material__topic=obj,
            is_completed=True
        ).count()

    def get_last_correct_answers(self, obj):
        return super().get_last_correct_answers(obj)

    def get_last_total_questions(self, obj):
        return super().get_last_total_questions(obj)

    def get_last_attempted_score(self, obj):
        return super().get_last_attempted_score(obj)


class StudyTopicListSerializer(TopicAttemptStatsMixin, serializers.ModelSerializer):
    """Lightweight — no nested materials, just counts + quiz stats."""
    material_count = serializers.IntegerField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.SerializerMethodField()
    last_correct_answers = serializers.SerializerMethodField()
    last_total_questions = serializers.SerializerMethodField()
    last_attempted_score = serializers.SerializerMethodField()

    class Meta:
        model = StudyTopic
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'material_count', 'question_count', 'completed_count', 'last_correct_answers', 'last_total_questions', 'last_attempted_score', 'created_at',
        ]

    def get_completed_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserMaterialProgress.objects.filter(
            user=request.user,
            material__topic=obj,
            is_completed=True
        ).count()

    def get_last_correct_answers(self, obj):
        return super().get_last_correct_answers(obj)

    def get_last_total_questions(self, obj):
        return super().get_last_total_questions(obj)

    def get_last_attempted_score(self, obj):
        return super().get_last_attempted_score(obj)


class MarkMaterialCompleteSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()


# ── Quiz Serializers ──────────────────────────────────────────

class QuestionSerializer(serializers.ModelSerializer):
    """For users taking the quiz — includes correct_option and topic."""
    topic_id = serializers.IntegerField(source='topic.id', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'topic_id', 'topic_title', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'order']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'topic', 'title', 'description',
            'question_count', 'questions', 'created_at',
        ]


class QuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)
    last_score = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'question_count', 'last_score', 'created_at']

    def get_last_score(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        attempt = QuizAttempt.objects.filter(
            user=request.user, quiz=obj
        ).order_by('-completed_at').first()
        if attempt:
            return {
                'score': attempt.score,
                'total': attempt.total_questions,
                'percentage': attempt.score_percentage,
            }
        return None


class QuizAnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'])


class TopicQuizSubmitSerializer(serializers.Serializer):
    """User submits all answers for a topic at once."""
    topic_id = serializers.IntegerField()
    answers = QuizAnswerSubmitSerializer(many=True)

    def validate_answers(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one answer is required.")
        return value


# Legacy serializer kept for backward compatibility
class QuizSubmitSerializer(serializers.Serializer):
    """User submits all answers at once."""
    quiz_id = serializers.IntegerField()
    answers = QuizAnswerSubmitSerializer(many=True)

    def validate_answers(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one answer is required.")
        return value


class QuizAttemptSerializer(serializers.ModelSerializer):
    score_percentage = serializers.FloatField(read_only=True)
    topic_id = serializers.IntegerField(source='topic.id', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'topic', 'topic_id', 'topic_title',
            'score', 'total_questions', 'score_percentage', 'completed_at',
        ]


class QuizAttemptDetailSerializer(serializers.ModelSerializer):
    """Full attempt with per-answer results."""
    score_percentage = serializers.FloatField(read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'topic', 'topic_title', 'score',
            'total_questions', 'score_percentage', 'completed_at', 'answers',
        ]

    def get_answers(self, obj):
        return [
            {
                'question_id': a.question.id,
                'question_text': a.question.text,
                'selected_option': a.selected_option,
                'correct_option': a.question.correct_option,
                'is_correct': a.is_correct,
            }
            for a in obj.answers.select_related('question').all()
        ]


class TopicQuizHistorySerializer(TopicAttemptStatsMixin, serializers.ModelSerializer):
    """Returns a topic with all quiz attempts nested under it."""
    attempts = serializers.SerializerMethodField()
    total_attempts = serializers.SerializerMethodField()
    best_score_percentage = serializers.SerializerMethodField()
    last_attempt = serializers.SerializerMethodField()

    class Meta:
        model = StudyTopic
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'total_attempts', 'best_score_percentage', 'last_attempt', 'attempts',
        ]

    def get_attempts(self, obj):
        attempts = self._get_user_attempts(obj)
        return [
            {
                'id': a.id,
                'topic_id': a.topic_id,
                'topic_title': a.topic.title if a.topic else None,
                'score': a.score,
                'total_questions': a.total_questions,
                'score_percentage': a.score_percentage,
                'completed_at': a.completed_at,
            }
            for a in attempts
        ]

    def get_total_attempts(self, obj):
        return self._get_user_attempts(obj).count()

    def get_last_attempt(self, obj):
        last_attempt = self._get_last_attempt(obj)
        if not last_attempt:
            return None
        return {
            'id': last_attempt.id,
            'topic_id': last_attempt.topic_id,
            'topic_title': last_attempt.topic.title if last_attempt.topic else None,
            'score': last_attempt.score,
            'total_questions': last_attempt.total_questions,
            'score_percentage': last_attempt.score_percentage,
            'completed_at': last_attempt.completed_at,
        }

    def get_best_score_percentage(self, obj):
        attempts = self._get_user_attempts(obj)
        if not attempts.exists():
            return 0
        return max(a.score_percentage for a in attempts)


# ── Admin Serializers ─────────────────────────────────────────

class AdminStudyTopicSerializer(serializers.ModelSerializer):
    material_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudyTopic
        fields = ['id', 'title', 'description', 'thumbnail', 'is_active', 'material_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminStudyMaterialSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    file = serializers.FileField(required=False, allow_null=True)
    pdf = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'topic', 'topic_title', 'title', 'description',
            'material_type', 'file', 'pdf', 'video_url', 'content',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminQuestionSerializer(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(
        queryset=StudyTopic.objects.all(), required=True
    )
    option_c = serializers.CharField(required=False, allow_blank=True)
    option_d = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Question
        fields = ['id', 'topic', 'quiz', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'order']
        read_only_fields = ['id']

    def validate(self, data):
        valid_options = []
        if data.get('option_a'):
            valid_options.append('A')
        if data.get('option_b'):
            valid_options.append('B')
        if data.get('option_c'):
            valid_options.append('C')
        if data.get('option_d'):
            valid_options.append('D')
        if len(valid_options) < 2:
            raise serializers.ValidationError('At least 2 options are required.')
        correct = data.get('correct_option')
        if correct and correct not in valid_options:
            raise serializers.ValidationError(f'Correct option must be one of: {valid_options}')
        return data


class AdminQuizSerializer(serializers.ModelSerializer):
    questions = AdminQuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'topic', 'title', 'description', 'is_active', 'question_count', 'questions', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminQuizAttemptSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    score_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'user_username', 'quiz', 'quiz_title',
            'score', 'total_questions', 'score_percentage', 'completed_at',
        ]
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class StudyTopic(models.Model):
    """Admin-managed topics that group materials and quizzes."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    thumbnail = models.ImageField(upload_to='study/thumbnails/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_topics'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

   
class StudyMaterial(models.Model):
    class MaterialType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        TEXT = 'text', 'Text'
        VIDEO = 'video', 'Video Link'

    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='materials'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    material_type = models.CharField(
        max_length=10, choices=MaterialType.choices, default=MaterialType.PDF
    )
    file = models.FileField(
        upload_to='study/materials/', null=True, blank=True,
        help_text='Upload general file (PDF or text file)'
    )
    pdf = models.FileField(
        upload_to='study/pdfs/', null=True, blank=True,
        help_text='Upload PDF file'
    )
    video_url = models.URLField(blank=True, default='')
    content = models.TextField(blank=True, default='', help_text='Text content if type is text')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_materials'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic.title} — {self.title}"


class UserMaterialProgress(models.Model):
    """Tracks which materials a user has read/downloaded."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='material_progress'
    )
    material = models.ForeignKey(
        StudyMaterial, on_delete=models.CASCADE, related_name='user_progress'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_material_progress'
        unique_together = ['user', 'material']

    def __str__(self):
        return f"{self.user.username} — {self.material.title}"


class Quiz(models.Model):
    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='quizzes'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """MCQ question — directly under a topic, 2–4 options, one correct."""
    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='questions',
        null=True, blank=True
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions',
        null=True, blank=True,
        help_text='Optional: legacy quiz grouping (deprecated)'
    )
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300, blank=True, default='')
    option_d = models.CharField(max_length=300, blank=True, default='')
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'quiz_questions'
        ordering = ['order']

    def clean(self):
        super().clean()
        valid_options = []
        if self.option_a:
            valid_options.append('A')
        if self.option_b:
            valid_options.append('B')
        if self.option_c:
            valid_options.append('C')
        if self.option_d:
            valid_options.append('D')
        if len(valid_options) < 2:
            raise ValidationError('At least 2 options are required.')
        if self.correct_option not in valid_options:
            raise ValidationError(f'Correct option must be one of the provided options: {valid_options}.')

    def __str__(self):
        return f"{self.topic.title if self.topic else 'No Topic'} — Q{self.order}"


class QuizAttempt(models.Model):
    """A user's completed quiz attempt with score — tied to a topic."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='attempts',
        null=True, blank=True
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='attempts',
        null=True, blank=True,
        help_text='Optional: legacy quiz reference (deprecated)'
    )
    score = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-completed_at']

    @property
    def score_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 1)

    def __str__(self):
        topic_title = self.topic.title if self.topic else 'No Topic'
        return f"{self.user.username} — {topic_title} — {self.score}/{self.total_questions}"


class QuizAnswer(models.Model):
    """Individual answer per question in an attempt."""
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers'
    )
    selected_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'quiz_answers'
        unique_together = ['attempt', 'question']
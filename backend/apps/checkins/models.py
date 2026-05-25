from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
from django.utils.text import slugify
import uuid


class Mood(models.Model):
    """Admin-managed mood options (e.g. Joyful, Calm, Hopeful, …)."""
    name = models.CharField(max_length=50, unique=True)
    emoji = models.CharField(max_length=255, blank=True)
    svg = models.FileField(upload_to='moods/svg/', blank=True, null=True)
    score = models.PositiveSmallIntegerField(
        help_text="Base score contribution (1-10)",
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'moods'
        ordering = ['name']

    def __str__(self):
        return self.name

    def build_svg(self):
        label = (self.emoji or self.name[:1] or '?').strip()
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{self.name}">
  <circle cx="32" cy="32" r="28" fill="#E8F5F2"/>
  <text x="32" y="40" text-anchor="middle" font-size="28" font-family="Arial, sans-serif" fill="#1F5D50">{label}</text>
</svg>'''

    def save(self, *args, **kwargs):
        if not self.svg:
            svg_content = self.build_svg().encode('utf-8')
            file_name = f"{slugify(self.name) or f'mood-{self.pk or uuid.uuid4().hex}'}.svg"
            self.svg.save(file_name, ContentFile(svg_content), save=False)
        super().save(*args, **kwargs)


class CheckIn(models.Model):
    """A single user check-in session."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkins'
    )
    mood = models.ForeignKey(
        Mood, on_delete=models.SET_NULL, null=True, related_name='checkins'
    )

    # Ratings 1-10
    mental_clarity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    emotional_balance = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    spiritual_wellness = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    physical_energy = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    # Optional fields (excluded from score if blank)
    gratitude = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    # Calculated score stored on save
    heart_balance_score = models.DecimalField(
        max_digits=4, decimal_places=2, editable=False, default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'checkins'
        ordering = ['-created_at']

    def calculate_score(self):
        """
        Heart Balance = (mood.score + avg(4 ratings)) / 2 * 10
        Optional bonus: +0.5 each for gratitude/notes, capped at 10.
        """
        avg_rating = (
            self.mental_clarity + self.emotional_balance +
            self.spiritual_wellness + self.physical_energy
        ) / 4

        mood_score = self.mood.score if self.mood else 5
        base = (mood_score + avg_rating) / 2

        bonus = 0
        if self.gratitude.strip():
            bonus += 0.5
        if self.notes.strip():
            bonus += 0.5

        return min(round(base + bonus, 2), 10)

    def save(self, *args, **kwargs):
        self.heart_balance_score = self.calculate_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.created_at.date()} — {self.heart_balance_score}"
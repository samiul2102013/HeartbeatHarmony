from django.db import migrations, models
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify
import uuid


def populate_mood_svg_files(apps, schema_editor):
    Mood = apps.get_model('checkins', 'Mood')

    for mood in Mood.objects.all():
        raw_svg = getattr(mood.svg, 'name', '') or ''
        if not raw_svg.strip().startswith('<svg'):
            continue

        label = (mood.emoji or mood.name[:1] or '?').strip()
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{mood.name}">
  <circle cx="32" cy="32" r="28" fill="#E8F5F2"/>
  <text x="32" y="40" text-anchor="middle" font-size="28" font-family="Arial, sans-serif" fill="#1F5D50">{label}</text>
</svg>'''

        file_name = f"moods/svg/{slugify(mood.name) or f'mood-{mood.pk}-{uuid.uuid4().hex[:8]}'} .svg"
        file_name = file_name.replace(' .svg', '.svg')
        saved_name = default_storage.save(file_name, ContentFile(svg_content.encode('utf-8')))
        mood.svg = saved_name
        mood.save(update_fields=['svg'])


class Migration(migrations.Migration):

    dependencies = [
        ('checkins', '0002_mood_svg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mood',
            name='svg',
            field=models.FileField(blank=True, null=True, upload_to='moods/svg/'),
        ),
        migrations.RunPython(populate_mood_svg_files, migrations.RunPython.noop),
    ]
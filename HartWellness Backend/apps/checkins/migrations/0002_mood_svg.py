from django.db import migrations, models


def populate_mood_svg(apps, schema_editor):
    Mood = apps.get_model('checkins', 'Mood')
    for mood in Mood.objects.all():
        label = (mood.emoji or mood.name[:1] or '?').strip()
        mood.svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{mood.name}">
  <circle cx="32" cy="32" r="28" fill="#E8F5F2"/>
  <text x="32" y="40" text-anchor="middle" font-size="28" font-family="Arial, sans-serif" fill="#1F5D50">{label}</text>
</svg>'''
        mood.save(update_fields=['svg'])


class Migration(migrations.Migration):

    dependencies = [
        ('checkins', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mood',
            name='svg',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.RunPython(populate_mood_svg, migrations.RunPython.noop),
    ]
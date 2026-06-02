from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Switch the Mood.svg upload path from 'moods/svg/' to 'moods/images/'.
    Existing files keep their stored paths (only new uploads use the new path).
    """

    dependencies = [
        ('checkins', '0004_alter_mood_emoji'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mood',
            name='svg',
            field=models.FileField(blank=True, null=True, upload_to='moods/images/'),
        ),
    ]

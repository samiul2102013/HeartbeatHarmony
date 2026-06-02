from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0006_habit_source_template'),
    ]

    operations = [
        migrations.CreateModel(
            name='HabitMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('material_type', models.CharField(choices=[('pdf', 'PDF'), ('text', 'Text'), ('video', 'Video Link'), ('audio', 'Audio')], default='pdf', max_length=10)),
                ('file', models.FileField(blank=True, help_text='Upload general file (PDF, audio, or text file)', null=True, upload_to='habits/materials/')),
                ('pdf', models.FileField(blank=True, help_text='Upload PDF file', null=True, upload_to='habits/pdfs/')),
                ('audio', models.FileField(blank=True, help_text='Upload audio file', null=True, upload_to='habits/audio/')),
                ('video_url', models.URLField(blank=True, default='')),
                ('content', models.TextField(blank=True, default='', help_text='Text content if type is text')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('habit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='habits.habit')),
            ],
            options={
                'db_table': 'habit_materials',
                'ordering': ['-created_at'],
            },
        ),
    ]
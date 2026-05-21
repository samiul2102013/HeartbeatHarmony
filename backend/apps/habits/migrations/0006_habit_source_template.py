from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0005_make_duration_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='source_template',
            field=models.ForeignKey(
                blank=True,
                help_text='Admin template this habit was created from, if any.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='adopted_habits',
                to='habits.habittemplate',
            ),
        ),
    ]

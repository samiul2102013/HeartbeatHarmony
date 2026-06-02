from django.db import migrations, models
import django.db.models.deletion


def keep_one_material_per_habit(apps, schema_editor):
    """For each habit with multiple HabitMaterial rows, keep the most recent
    (highest id) and delete the rest. Required before the OneToOne constraint
    can be applied — otherwise the migration would fail on duplicate rows."""
    HabitMaterial = apps.get_model('habits', 'HabitMaterial')
    seen_habits = set()
    # Iterate from newest to oldest; first row we see for a habit is the keeper.
    for material in HabitMaterial.objects.order_by('-id'):
        if material.habit_id in seen_habits:
            material.delete()
        else:
            seen_habits.add(material.habit_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0010_remove_habitmaterial_pdf_remove_habitmaterial_video_and_more'),
    ]

    operations = [
        # 1) Dedupe existing data: keep one material per habit, delete the rest.
        migrations.RunPython(keep_one_material_per_habit, noop_reverse),

        # 2) Convert FK -> OneToOneField. This adds a UNIQUE constraint on habit_id.
        migrations.AlterField(
            model_name='habitmaterial',
            name='habit',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='material',
                to='habits.habit',
            ),
        ),
    ]

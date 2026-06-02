from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_rating_user_check_ins_user_quiz_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='institute_name',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_user_username'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE users ADD COLUMN IF NOT EXISTS institute_name varchar(150) NOT NULL DEFAULT '';",
            reverse_sql="ALTER TABLE users DROP COLUMN IF EXISTS institute_name;",
        ),
    ]

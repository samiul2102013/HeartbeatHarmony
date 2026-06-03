import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check the admin habit material endpoint behavior
cmd = '''docker exec hartbeat-backend bash -c 'python -c "
import json, django; import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"config.settings\")
import django; django.setup()
from apps.habits.serializers import AdminHabitMaterialSerializer
print(\"Serializer fields:\", list(AdminHabitMaterialSerializer().fields.keys()))
print(\"HabitMaterial model:\", AdminHabitMaterialSerializer.Meta.model.__name__)
from apps.habits.views import HabitMaterialListCreateView
from apps.habits.models import HabitMaterial, Habit
print(\"HabitMaterial FK fields:\", [f.name for f in HabitMaterial._meta.fields if f.is_relation])
" 2>&1' '''
stdin, stdout, stderr = c.exec_command(cmd)
print(stdout.read().decode()[:1000])
c.close()

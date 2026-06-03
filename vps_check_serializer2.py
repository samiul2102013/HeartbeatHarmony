import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = r'''import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, "/app")
import django; django.setup()
from apps.habits.serializers import AdminHabitMaterialSerializer
from apps.habits.models import HabitMaterial, Habit, HabitTemplate
import json
s = AdminHabitMaterialSerializer()
print("Serializer fields:", list(s.fields.keys()))
print("Model:", s.Meta.model.__name__)
print("Habit field type:", type(s.fields["habit"]).__name__)
# Check the habit field
from rest_framework import serializers
hf = s.fields["habit"]
print("Habit field class:", type(hf).__name__)
if hasattr(hf, 'queryset'):
    print("Habit field queryset model:", hf.queryset.model.__name__)
'''

sftp = c.open_sftp()
with sftp.open("/tmp/check_serializer.py", "w") as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/check_serializer.py hartbeat-backend:/tmp/check_serializer.py && docker exec hartbeat-backend python /tmp/check_serializer.py 2>&1")
print(stdout.read().decode()[:2000])
c.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.checkins.models import Mood
import os

for m in Mood.objects.all():
    svg_path = m.svg.name if m.svg else 'NO FILE'
    file_exists = os.path.isfile(m.svg.path) if m.svg else False
    print(f'ID={m.id}, Name={m.name}, SVG={svg_path}, FileExists={file_exists}')
print(f'Total moods: {Mood.objects.count()}')
" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Mood SVGs ===")
print(out[:2000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

client.close()

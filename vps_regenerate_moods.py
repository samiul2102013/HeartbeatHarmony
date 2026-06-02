import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.checkins.models import Mood
import os

for m in Mood.objects.all():
    old_path = m.svg.name if m.svg else 'N/A'
    # Clear the svg field so save() regenerates it
    m.svg = None
    m.save()  # This triggers auto-generation of SVG
    new_path = m.svg.name if m.svg else 'FAILED'
    file_exists = os.path.isfile(m.svg.path) if m.svg else False
    print(f'Mood: {m.name} -> Old: {old_path} -> New: {new_path} -> Exists: {file_exists}')
" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Regenerated Mood SVGs ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

# Now test a mood SVG URL
cmd2 = "curl -s -o /dev/null -w 'HTTP:%{http_code}' http://localhost:8005/media/moods/svg/happyness.svg 2>/dev/null"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Happyness SVG: {out}")

client.close()

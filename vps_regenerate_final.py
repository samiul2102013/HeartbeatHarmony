import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Wait for backend to be ready
for i in range(10):
    stdin, stdout, stderr = client.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/admin/login/ 2>/dev/null')
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    if out == '200':
        print(f"Backend ready after {i+1}s")
        break
    print(f"Waiting... ({i+1}s)")
    time.sleep(1)
    client.close()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Regenerate SVGs
cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.checkins.models import Mood
import os

for m in Mood.objects.all():
    old = m.svg.name if m.svg else 'NONE'
    m.svg = None
    m.save()
    new = m.svg.name if m.svg else 'FAILED'
    exists = os.path.isfile(m.svg.path) if m.svg else False
    print(f'{m.name}: {old} -> {new} (exists={exists})')
" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Regenerated SVGs ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

# Test URLs
stdin, stdout, stderr = client.exec_command('curl -s -o /dev/null -w "Happyness:%{http_code}" http://localhost:8005/media/moods/svg/happyness.svg 2>/dev/null')
print(stdout.read().decode('utf-8', errors='ignore').strip())

stdin, stdout, stderr = client.exec_command('curl -s -o /dev/null -w " Mindfullness:%{http_code}" http://localhost:8005/media/moods/svg/mindfullness.svg 2>/dev/null')
print(stdout.read().decode('utf-8', errors='ignore').strip())

client.close()

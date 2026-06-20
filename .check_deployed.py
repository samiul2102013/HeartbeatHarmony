import paramiko, base64
host, user, password = '2.24.115.93', 'root', 'HartbeatWellness@Portia123'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password, timeout=10)

script = '''
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, "/app")
django.setup()
from apps.habits.views import HabitMarkDoneView
import inspect
lines, _ = inspect.getsourcelines(HabitMarkDoneView.post)
print("".join(lines))
'''

b64 = base64.b64encode(script.encode()).decode()
stdin, stdout, stderr = client.exec_command(f"docker exec hartbeat-backend bash -c 'echo {b64} | base64 -d > /tmp/ch.py && cd /app && python /tmp/ch.py'", timeout=30)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(out)
if err: print('ERR:', err[:800])
client.close()

import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Execute from /app directory inside container
cmd = '''docker exec hartbeat-backend bash -c 'cd /app && python -c "
import sys
sys.path.insert(0, \"/app\")
from django.db import connection
from apps.accounts.models import User
print(\"=== DATABASE CHECK ===\")
print(\"Tables:\", list(connection.introspection.table_names()))
print(\"=== USERS ===\")
users = list(User.objects.all())
print(f\"Count: {len(users)}\")
for u in users[:5]:
    print(f\"  {u.email} role={u.role} active={u.is_active} verified={u.email_verified}\"
" 2>&1' '''
stdin, stdout, stderr = c.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print("OUTPUT:")
print(out)
if err:
    print("ERROR:", err)

c.close()
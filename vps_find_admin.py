import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = """docker exec hartbeat-backend python manage.py shell << 'PYEOF'
from apps.accounts.models import User

# Search with exact match
for u in User.objects.filter(email__icontains='ICSNCardiology'):
    print(f'FOUND: email=\'{u.email}\' (exact repr: {repr(u.email)})')
    print(f'  username={u.username}, role={u.role}')

# Also search for admin_hartbeat
u = User.objects.filter(username='admin_hartbeat').first()
if u:
    print(f'By username: email={repr(u.email)}, role={u.role}')
else:
    print('admin_hartbeat NOT FOUND')
PYEOF"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Search ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

client.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User
# Fix email to lowercase
u = User.objects.get(username='admin_hartbeat')
print(f'Before: {repr(u.email)}')
u.email = u.email.lower()
u.save()
print(f'After: {repr(u.email)}')
print(f'Role={u.role}, Staff={u.is_staff}, Super={u.is_superuser}, Verified={u.email_verified}')" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Fix Email ===")
print(out[:500] if out else "(empty)")
if err:
    print(f"[ERR] {err[:300]}")

client.close()

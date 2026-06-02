import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check all admin accounts verified status
cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User;
admins = User.objects.filter(is_staff=True);
for u in admins:
    print(f'{u.email} -> Verified={u.email_verified}, Staff={u.is_staff}, Superuser={u.is_superuser}')" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Admin Accounts ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:300]}")

client.close()

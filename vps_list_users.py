import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check users inside backend container
cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User;
users = User.objects.all();
print(f'Total users: {users.count()}');
for u in users:
    print(f'ID={u.id}, Email={u.email}, Username={u.username}, Role={u.role}, Verified={u.email_verified}, Staff={u.is_staff}, Superuser={u.is_superuser} Active={u.is_active}')" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Users ===")
print(out[:2000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

client.close()

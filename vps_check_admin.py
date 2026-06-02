import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check if support@ICSNCardiology.org exists
cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User;
u = User.objects.filter(email='support@ICSNCardiology.org').first();
if u:
    print(f'EXISTS: ID={u.id}, Email={u.email}, Username={u.username}, Role={u.role}, Staff={u.is_staff}, Superuser={u.is_superuser}')
else:
    print('NOT_FOUND')
" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Check support@ICSNCardiology.org ===")
print(out[:500] if out else "(empty)")
if err:
    print(f"[ERR] {err[:300]}")
print()

# Check for any superuser/admin
cmd2 = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User;
admins = User.objects.filter(is_staff=True)|User.objects.filter(is_superuser=True);
print(f'Admin count: {admins.count()}');
for a in admins:
    print(f'ID={a.id}, Email={a.email}, Staff={a.is_staff}, Superuser={a.is_superuser}')" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Existing Admins ===")
print(out[:500] if out else "(empty)")
if err:
    print(f"[ERR] {err[:300]}")

client.close()

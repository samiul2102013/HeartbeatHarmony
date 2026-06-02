import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Use manage.py shell -c with compact Python code
cmd = """docker exec hartbeat-backend python manage.py shell -c "exec(open('/tmp/check_users.py').read())" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Check Users ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

# Now check for the support email
cmd2 = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User
users = User.objects.filter(email__icontains='ICSN')
print(f'Found: {users.count()}')
for u in users:
    print(u.email, u.role, u.is_staff, u.is_superuser, u.email_verified)
" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print()
print("=== Search ICSN ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

client.close()

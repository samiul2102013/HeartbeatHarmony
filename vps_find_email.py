import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check what email exists
cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.accounts.models import User;
for email in ['support@icsncardiology.org', 'support@icsncardioloy.org', 'kodevio@gmail.com', 'kkodevio@gmail.com']:
    u = User.objects.filter(email__iexact=email).first()
    if u:
        print(f'FOUND: {u.email} -> ID={u.id}, Verified={u.email_verified}, Staff={u.is_staff}, Superuser={u.is_superuser}, Active={u.is_active}')
    else:
        print(f'NOT_FOUND: {email}')
" 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Email Search ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:300]}")

client.close()

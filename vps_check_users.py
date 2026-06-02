import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test login API response directly
cmd = """curl -s -X POST http://localhost:8005/api/auth/login/ -H "Content-Type: application/json" -d '{"email":"admin@admin.com","password":"admin"}' 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print("=== Login test (admin/admin) ===")
print(out[:1000])
print()

# Check what users exist in the database
cmd2 = "cd /root/hartbeat-harmony && python backend/manage.py shell -c \"from apps.accounts.models import User; users = User.objects.all(); print(f'Total users: {users.count()}'); [print(f'ID={u.id}, Email={u.email}, Username={u.username}, Role={u.role}, Verified={u.email_verified}, Active={u.is_active}, Staff={u.is_staff}, Superuser={u.is_superuser}') for u in users]\" 2>/dev/null"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Users in database ===")
print(out[:1500] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

client.close()

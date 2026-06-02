import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Try creating admin user, with full error output
cmd = "docker exec hartbeat-backend sh -c 'echo \"from apps.accounts.models import User; User.objects.create_user(email=\\\"support@ICSNCardiology.org\\\", password=\\\"Admin@123456\\\", role=\\\"admin\\\", is_verified=True, is_active=True)\" | python manage.py shell' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("OUT:", out)
if err: print("ERR:", err)

# Verify
cmd2 = "docker exec hartbeat-backend sh -c 'echo \"from apps.accounts.models import User; u=User.objects.filter(email=\\\"support@ICSNCardiology.org\\\").first(); print(f\\\"exists={bool(u)} role={u.role if u else None}\\\")\" | python manage.py shell' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd2)
print("Verify:", stdout.read().decode().strip())

client.close()

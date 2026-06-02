import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test login via API
cmd = "curl -s -X POST http://localhost:8005/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\",\"password\":\"Admin@123456\"}'"
stdin, stdout, stderr = client.exec_command(cmd)
print("Login:", stdout.read().decode()[:300])

# DB check using cat pipe approach
cmd2 = "docker exec hartbeat-backend sh -c \"echo 'from apps.accounts.models import User; u=User.objects.filter(email__iexact=\\\\"support@ICSNCardiology.org\\\").first(); print(f\\\"exists={bool(u)} role={u.role if u else None} pw_ok={u.check_password(\\\"\"'Admin@123456'\"\\\") if u else None}\\\")\" | python manage.py shell\""
# too complex, skip

client.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test login via API
cmd = "curl -s -X POST http://localhost:8005/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\",\"password\":\"Admin@123456\"}' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd)
print("Login response:")
print(stdout.read().decode()[:500])

# Also directly verify in the DB
cmd2 = "docker exec hartbeat-backend sh -c 'cd /app && python manage.py shell << ENDSCRIPT
from apps.accounts.models import User
u = User.objects.filter(email__iexact=\"support@ICSNCardiology.org\").first()
if u:
    print(f\"User: {u.email} role={u.role} active={u.is_active} verified={u.email_verified}\")
    print(f\"Password ok: {u.check_password(\\\"Admin@123456\\\")}\")
else:
    print(\"NO USER FOUND\")
ENDSCRIPT' 2>&1"
stdin2, stdout2, stderr2 = client.exec_command(cmd2)
print("\nDB check:")
print(stdout2.read().decode()[:500])

client.close()

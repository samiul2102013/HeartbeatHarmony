import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = c.exec_command("docker ps --filter name=hartbeat-backend --format '{{.Names}} {{.Status}}'")
print("Backend:", stdout.read().decode().strip())

stdin, stdout, stderr = c.exec_command("docker exec hartbeat-backend curl -s -X POST http://localhost:8005/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\",\"password\":\"Admin@123456\"}' 2>&1")
out = stdout.read().decode()
print("Login response:", out[:400] if out else "(empty)")

c.close()

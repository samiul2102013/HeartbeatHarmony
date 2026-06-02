import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test login from host (port 8005 is published or internal?)
stdin, stdout, stderr = c.exec_command("curl -s -X POST http://localhost:8005/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\",\"password\":\"Admin@123456\"}' 2>&1")
out = stdout.read().decode()
print("Host login:", out[:400] if out else "(empty)")
c.close()

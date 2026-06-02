import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Try through Traefik on port 443 using the domain
stdin, stdout, stderr = c.exec_command("curl -sk -X POST https://api.heartbeatharmony.tech/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\",\"password\":\"Admin@123456\"}' 2>&1")
out = stdout.read().decode()
print("Login via Traefik:", out[:500] if out else "(empty)")
c.close()

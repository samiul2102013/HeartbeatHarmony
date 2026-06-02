import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test with uppercase email
stdin, stdout, stderr = c.exec_command("curl -sk -X POST https://api.heartbeatharmony.tech/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\",\"password\":\"Admin@123456\"}' 2>&1")
print("Uppercase:", stdout.read().decode()[:300])

# Test with lowercase email
stdin2, stdout2, stderr2 = c.exec_command("curl -sk -X POST https://api.heartbeatharmony.tech/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\":\"support@icsncardiology.org\",\"password\":\"Admin@123456\"}' 2>&1")
print("Lowercase:", stdout2.read().decode()[:300])
c.close()

import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Get admin token first
stdin, stdout, stderr = c.exec_command('curl -sk -X POST https://api.heartbeatharmony.tech/api/auth/login/ -H "Content-Type: application/json" -d \'{"email":"support@icsncardiology.org","password":"Admin@123456"}\' 2>&1')
import json
out = stdout.read().decode()
token_data = json.loads(out)
access = token_data["data"]["access"]

# Call topics endpoint
cmd = f'curl -sk https://api.heartbeatharmony.tech/api/admin/study/topics/ -H "Authorization: Bearer {access}" 2>&1'
stdin, stdout, stderr = c.exec_command(cmd)
print("Topics API response:")
print(stdout.read().decode()[:1000])
c.close()

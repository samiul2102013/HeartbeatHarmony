import paramiko
host, user, password = '2.24.115.93', 'root', 'HartbeatWellness@Portia123'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password, timeout=10)

stdin, stdout, stderr = client.exec_command('docker logs hartbeat-backend --tail=50 2>&1', timeout=15)
print(stdout.read().decode('utf-8', errors='replace').strip())
client.close()

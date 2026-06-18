import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

stdin, stdout, stderr = client.exec_command('docker ps --filter name=hartbeat-frontend --format "{{.Names}} {{.Status}}"')
print(stdout.read().decode().strip())
client.close()

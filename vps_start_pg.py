import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = 'systemctl start postgresql && systemctl enable postgresql && systemctl status postgresql --no-pager 2>&1 | head -10'
stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode()[:500])
client.close()

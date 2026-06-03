import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = 'docker exec hartbeat-postgres psql -U hartbeat -d hartbeat_db -c "\\dt" 2>&1'
stdin, stdout, stderr = c.exec_command(cmd)
print(stdout.read().decode())
c.close()

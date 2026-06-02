import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = c.exec_command("ls -la /etc/dokploy/compose/ 2>/dev/null && echo '---' && ls /etc/dokploy/compose/*/code/ 2>/dev/null || echo 'nofiles'")
print(stdout.read().decode()[:1000])
c.close()

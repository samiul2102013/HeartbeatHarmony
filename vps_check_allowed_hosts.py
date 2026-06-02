import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = c.exec_command("docker inspect hartbeat-backend --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep ALLOWED_HOSTS")
print(stdout.read().decode()[:500])
c.close()

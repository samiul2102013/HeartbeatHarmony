import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = c.exec_command("cat /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code/docker-compose.dokploy.yml")
print(stdout.read().decode())
c.close()

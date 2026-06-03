import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = c.exec_command("grep -A3 'env_file' /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code/docker-compose.dokploy.yml 2>&1")
print("env_file:", stdout.read().decode()[:500])

stdin2, stdout2, stderr2 = c.exec_command("ls /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code/backend/.env 2>&1")
print("backend/.env exists:", stdout2.read().decode())

c.close()

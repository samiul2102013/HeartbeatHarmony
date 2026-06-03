import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check if Dokploy compose directory is a symlink
stdin, stdout, stderr = c.exec_command("ls -la /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code/ 2>&1 | head -5")
print(stdout.read().decode())

# Check backend Dockerfile path
stdin2, stdout2, stderr2 = c.exec_command("ls -la /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code/backend/Dockerfile 2>&1")
print(stdout2.read().decode())

# Rebuild using the Dokploy compose file directly
stdin3, stdout3, stderr3 = c.exec_command("cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -p hartbeatstack-hartbeatstack-buv5uf build backend 2>&1")
out = stdout3.read().decode()
err = stderr3.read().decode()
if out: print("Build:", out[:500])
if err: print("Build ERR:", err[:300])

c.close()

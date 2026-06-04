import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && git fetch --force origin && git reset --hard origin/main",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml build --no-cache backend",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d backend",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml build --no-cache frontend",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d frontend",
]

for cmd in commands:
    print(f"> {cmd}")
    stdin, stdout, stderr = c.exec_command(cmd, timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out[:500])
    if err: print("ERR:", err[:300])
    print()

c.close()

import paramiko
import time

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

commands = [
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && git fetch --force origin && git reset --hard origin/main",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml build backend 2>&1 | tail -20",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml build frontend 2>&1 | tail -20",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d backend",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d frontend",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d nginx",
]

for cmd in commands:
    print(f"Running: {cmd[:80]}...")
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out[-2000:] if len(out) > 2000 else out)
    if err:
        print("STDERR:", err[-1000:])
    if exit_status != 0:
        print(f"Command failed with exit status {exit_status}")
    print()

# Run migrations
print("Running migrations...")
stdin, stdout, stderr = client.exec_command("docker exec hartbeat-backend python manage.py migrate")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print('STDERR:', err)

print("Deploy complete!")
client.close()

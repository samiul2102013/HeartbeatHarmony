import paramiko
import sys

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

commands = [
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && git fetch --force origin && git reset --hard origin/main",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml build --no-cache frontend 2>&1 | tail -40",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d frontend",
]

for cmd in commands:
    print(f"Running: {cmd[:60]}...")
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        lines = out.split('\n')
        for line in lines[-20:]:
            print(line.encode('ascii', errors='replace').decode('ascii'))
    if err:
        lines = err.split('\n')
        for line in lines[-10:]:
            print('ERR:', line.encode('ascii', errors='replace').decode('ascii'))
    print()

print("Done!")
client.close()

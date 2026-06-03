import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    "cd /root/hartbeat-harmony && git pull origin main",
    "cd /root/hartbeat-harmony && docker compose -p hartbeatstack-hartbeatstack-buv5uf build backend",
    "cd /root/hartbeat-harmony && docker compose -p hartbeatstack-hartbeatstack-buv5uf up -d backend",
    "cd /root/hartbeat-harmony && docker compose -p hartbeatstack-hartbeatstack-buv5uf build frontend",
    "cd /root/hartbeat-harmony && docker compose -p hartbeatstack-hartbeatstack-buv5uf up -d frontend",
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

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Stop backend, pull, rebuild, restart
commands = [
    'cd /root/hartbeat-harmony && git pull origin main 2>&1 | tail -5',
    'cd /root/hartbeat-harmony && docker compose -p hartbeat -f docker-compose.deploy.yml build backend 2>&1 | tail -5',
    'cd /root/hartbeat-harmony && docker compose -p hartbeat -f docker-compose.deploy.yml up -d backend 2>&1 | tail -10',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {cmd[:60]} ===")
    print(out[-1000:] if len(out) > 1000 else out)
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

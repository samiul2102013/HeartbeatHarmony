import paramiko, os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'cd /root/hartbeat-harmony && git clone https://github.com/samiul2102013/HeartbeatHarmony.git . 2>&1 || (git fetch origin && git reset --hard origin/main)',
    'ls -la /root/hartbeat-harmony/',
    'ls /root/hartbeat-harmony/docker-compose.dokploy.yml 2>/dev/null && echo DOKPLOY_COMPOSE_EXISTS || echo MISSING',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f"=== {cmd[:80]} ===")
    print(out if out else "(empty)")
    if err:
        print(f"[ERR] {err[:200]}")
    print()

client.close()

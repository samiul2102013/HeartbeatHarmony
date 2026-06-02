import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Stop any existing containers with same names, then deploy
commands = [
    'docker rm -f hartbeat-redis hartbeat-backend hartbeat-frontend 2>/dev/null; echo "Cleaned old containers"',
    'cd /root/hartbeat-harmony && docker compose -p hartbeat -f docker-compose.deploy.yml up -d 2>&1 | tail -30',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {cmd[:50]} ===")
    print(out[-2000:] if len(out) > 2000 else out)
    if err:
        print(f"[ERR] {err[:500]}")
    print()

client.close()

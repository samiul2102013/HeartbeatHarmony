import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# First build the images
commands = [
    'cd /root/hartbeat-harmony && docker compose -f docker-compose.dokploy.yml --env-file .env.dokploy build --no-cache backend 2>&1 | tail -30',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== BUILD ===")
    print(out[:3000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:500]}")
    print()

client.close()

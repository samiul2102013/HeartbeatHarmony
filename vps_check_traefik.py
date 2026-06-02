import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check Traefik ACME status
commands = [
    'docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>/dev/null | head -100',
    'docker logs dokploy-traefik --tail 30 2>&1 | grep -i "acme\|certif\|letsencrypt\|error\|challenge" | head -20',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {i+1} ===")
    print(out[:2000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

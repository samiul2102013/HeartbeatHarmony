import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'docker logs dokploy-traefik --tail 50 2>&1 | grep -i "admin\|acme\|certif\|frontend\|multiple" | head -20',
    "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>/dev/null | grep -E '\"main\"|\"Domain\"|\"sans\"' | head -10",
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(out[:2000] if out else '(empty)')
    if err:
        print(f'ERR: {err[:300]}')
    print()

client.close()

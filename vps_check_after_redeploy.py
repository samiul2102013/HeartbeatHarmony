import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'docker logs dokploy-traefik --tail 100 2>&1 | grep -i "admin\.heartbeat\|acme\|certif\|frontend" | head -20',
    "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>/dev/null | grep -E '\"main\"|\"Domain\"|\"api\.\"|\"admin\.\"' | head -10",
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"OUT:\n{out[:2000] if out else '(empty)'}")
    if err:
        print(f"ERR: {err[:300]}")
    print()

client.close()

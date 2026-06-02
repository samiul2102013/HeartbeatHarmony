import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check Dokploy Traefik config
    'docker inspect dokploy-traefik --format "{{range .Args}}{{println .}}{{end}}" 2>/dev/null',
    # Check Traefik config files
    'docker exec dokploy-traefik ls /etc/traefik/ 2>/dev/null',
    'docker exec dokploy-traefik ls /etc/traefik/dynamic/ 2>/dev/null',
    # Check which providers Traefik uses  
    'docker exec dokploy-traefik cat /etc/traefik/traefik.yml 2>/dev/null || docker exec dokploy-traefik cat /traefik.yml 2>/dev/null || echo NO_TRAEFIK_YML',
    # Check for dynamic config files
    'docker exec dokploy-traefik find / -name "*.yml" -path "*traefik*" 2>/dev/null',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== CMD {i+1} ===")
    print(out[:1500] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

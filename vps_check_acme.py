import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check certificates directory
    'docker exec dokploy-traefik ls -la /etc/dokploy/traefik/dynamic/certificates/ 2>/dev/null',
    # Check acme.json for any certificates at all (different format)
    "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>/dev/null | grep -E '\"Domain\"|\"main\"|\"api\.\"|\"admin\.\"' | head -10",
    # Check cert directory for files with our domain names
    "docker exec dokploy-traefik ls /etc/dokploy/traefik/dynamic/certificates/ 2>/dev/null | head -20",
    # Check Traefik full config
    "docker exec dokploy-traefik cat /etc/traefik/traefik.yml 2>/dev/null",
    # Check what Traefik sees as its current certificate stores
    "docker exec dokploy-traefik traefik healthcheck 2>/dev/null && echo OK || echo FAIL",
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"CMD: {cmd[:60]}...")
    print(out[:1500] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

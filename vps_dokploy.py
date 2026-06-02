import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check current Docker Swarm status
    'docker node ls 2>/dev/null',
    'docker service ls 2>/dev/null',
    # Check if there are any existing services using dokploy-network
    'docker network inspect dokploy-network --format "{{range .Containers}}{{.Name}} {{end}}" 2>/dev/null',
    # Check Dokploy container logs for admin info
    'docker logs $(docker ps --format "{{.Names}}" | grep "dokploy.1" | head -1) 2>&1 | head -50',
    # Check if there's a dokploy config file with admin credentials
    'cat /etc/dokploy/config.json 2>/dev/null || echo NODOKPLOYCONFIG',
    # Check for setup files
    'ls -la /root/dokploy* 2>/dev/null || ls -la /tmp/dokploy* 2>/dev/null || echo NOSETUPFILES',
    # Check Traefik dynamic config
    'docker exec $(docker ps --format "{{.Names}}" | grep traefik | head -1) cat /etc/traefik/traefik.yml 2>/dev/null || docker exec $(docker ps --format "{{.Names}}" | grep traefik | head -1) cat /traefik.yml 2>/dev/null || echo NO_TRAEFIK_CONFIG',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f"=== {cmd[:80]} ===")
    print(out[:1000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

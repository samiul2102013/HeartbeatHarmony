import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check how Dokploy deployed our services
commands = [
    'docker service ls 2>/dev/null | grep -i "hartbeat\|stack"',
    # Check if services are Docker Swarm services or regular containers
    'docker ps --filter name=hartbeat --format "{{.Names}} {{.Image}}"',
    # Check labels on the containers
    'docker inspect hartbeat-backend --format "{{json .Config.Labels}}" 2>/dev/null | head -200',
    'docker inspect hartbeat-frontend --format "{{json .Config.Labels}}" 2>/dev/null | head -200',
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

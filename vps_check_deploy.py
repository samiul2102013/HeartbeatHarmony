import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check existing images and verify compose file
commands = [
    'docker images --format "{{.Repository}}:{{.Tag}}" | head -20',
    'wc -l /root/hartbeat-harmony/docker-compose.deploy.yml',
    'tail -5 /root/hartbeat-harmony/docker-compose.deploy.yml',
    # Try deploying with compose - first check if compose is valid
    'cd /root/hartbeat-harmony && docker compose -p hartbeat -f docker-compose.deploy.yml config 2>&1 | head -30',
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

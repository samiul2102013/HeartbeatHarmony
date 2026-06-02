import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'git --version 2>/dev/null',
    'which rsync 2>/dev/null',
    'which scp 2>/dev/null',
    'mkdir -p /root/hartbeat-harmony && echo DIR_CREATED',
    'docker inspect dokploy-traefik --format "{{json .Config.Labels}}" 2>/dev/null | head -100',
    'ls -la /root/',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f"=== {cmd} ===")
    print(out if out else "(empty)")
    if err:
        print(f"[ERR] {err}")
    print()

client.close()

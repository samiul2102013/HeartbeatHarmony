import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'hostname',
    'docker --version 2>/dev/null',
    'docker compose version 2>/dev/null',
    'docker ps -a 2>/dev/null',
    'cat /etc/os-release 2>/dev/null | head -3',
    'ss -tlnp 2>/dev/null | head -15',
    'df -h / 2>/dev/null',
    'free -m 2>/dev/null',
    'nproc',
    'ls /opt/ 2>/dev/null',
    'systemctl list-units --type=service --state=running 2>/dev/null | grep -i "dokploy\|docker\|traefik"',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command('$HOME/.cargo/env 2>/dev/null; ' + cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f"$ {cmd}")
    if out:
        print(out)
    if err:
        print(f"[stderr] {err}")
    print("---")

client.close()

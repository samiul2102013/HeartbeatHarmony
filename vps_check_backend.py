import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'docker ps --filter name=hartbeat-backend --format "{{.Names}} {{.Status}}"',
    'docker logs hartbeat-backend --tail 20 2>&1',
    'docker inspect hartbeat-backend --format "{{.State.Health.Status}}" 2>/dev/null',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {i+1} ===")
    print(out[:500] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:200]}")
    print()

client.close()

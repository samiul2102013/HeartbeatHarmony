import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"',
    'docker logs hartbeat-backend --tail 20 2>&1',
    'sleep 5 && curl -s http://localhost:8005/admin/login/ 2>/dev/null | head -5',
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:3004/ 2>/dev/null',
    'curl -s http://localhost:8005/api/schema/ 2>/dev/null | head -5',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== CHECK {i+1} ===")
    print(out[:2000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

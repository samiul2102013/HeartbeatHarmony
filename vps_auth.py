import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Try to register a new admin (first-time setup)
    """curl -s -X POST http://localhost:3000/api/auth/register -H "Content-Type: application/json" -d '{"name":"Admin","email":"admin@hartbeat.com","password":"Admin123!"}' 2>/dev/null""",
    # Try login
    """curl -s -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@hartbeat.com","password":"Admin123!"}' 2>/dev/null""",
    # Check if Dokploy has env vars with credentials
    'docker exec $(docker ps --format "{{.Names}}" | grep dokploy.1 | head -1) env 2>/dev/null | sort | head -30',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== CMD {i+1} ===")
    print(out[:1000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:200]}")
    print()

client.close()

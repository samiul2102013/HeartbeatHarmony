import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check backend logs for errors
    'docker logs hartbeat-backend --tail 30 2>&1',
    # Frontend test - follow redirect
    'curl -sL -o /dev/null -w "%{http_code}" http://localhost:3004/ 2>/dev/null',
    # Test backend API login endpoint
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/api/auth/login/ -X POST -H "Content-Type: application/json" -d "{}" 2>/dev/null',
    # Test WebSocket/Socket.IO endpoint
    'curl -s http://localhost:8005/socket.io/?EIO=4 -o /dev/null -w "%{http_code}" 2>/dev/null',
    # Check Redis connection
    'docker exec hartbeat-redis redis-cli ping 2>/dev/null',
    # Test external access to backend
    'curl -s -o /dev/null -w "%{http_code}" http://2.24.115.93:8005/admin/login/ 2>/dev/null',
    'curl -s -o /dev/null -w "%{http_code}" http://2.24.115.93:3004/ 2>/dev/null',
    # Check collectstatic output
    'docker logs hartbeat-backend 2>&1 | grep -i "collect\|static\|error\|Error\|Traceback" | head -10',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {i+1} ===")
    print(out[:1000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:200]}")
    print()

client.close()

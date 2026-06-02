import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test SMTP by calling forgot-password endpoint
cmd = """curl -s -X POST http://localhost:8005/api/auth/forgot-password/ -H "Content-Type: application/json" -d '{"email":"support@ICSNCardiology.org"}' 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print(f"=== SMTP Test (forgot-password) ===")
print(out if out else "(empty)")
if err:
    print(f"[ERR] {err[:300]}")
print()

# Check backend logs for SMTP errors
cmd2 = "docker logs hartbeat-backend 2>&1 | grep -i 'email\|smtp\|error\|Error\|Password' | tail -10"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"=== Backend Email Logs ===")
print(out if out else "(no email logs)")
print()

# Test WebSocket by connecting to Socket.IO
cmd3 = "curl -s http://localhost:8005/socket.io/?EIO=4 -o /dev/null -w 'HTTP:%{http_code}' 2>/dev/null && echo '' && curl -s http://localhost:8005/socket.io/?EIO=4 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -o /dev/null -w 'WS_UPGRADE:%{http_code}' 2>/dev/null"
stdin, stdout, stderr = client.exec_command(cmd3)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"=== WebSocket Test ===")
print(out if out else "(empty)")

client.close()

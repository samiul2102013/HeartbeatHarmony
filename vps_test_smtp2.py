import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test SMTP with timeout
cmd = "timeout 15 curl -s -X POST http://localhost:8005/api/auth/forgot-password/ -H 'Content-Type: application/json' -d '{\"email\":\"support@ICSNCardiology.org\"}' 2>/dev/null || echo TIMEOUT"
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"=== SMTP Test ===")
print(out[:500] if out else "(empty)")
print()

# Check backend logs quickly
cmd2 = "docker logs hartbeat-backend 2>&1 | tail -20"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"=== Backend Logs (tail) ===")
print(out[:1500] if out else "(empty)")

client.close()

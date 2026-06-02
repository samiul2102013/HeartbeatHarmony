import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test login
cmd = """curl -s -X POST http://localhost:8005/api/auth/login/ -H "Content-Type: application/json" -d '{"email":"support@ICSNCardiology.org","password":"Admin@123456"}' 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Login Test ===")
print(out[:1000] if out else "(empty)")

client.close()

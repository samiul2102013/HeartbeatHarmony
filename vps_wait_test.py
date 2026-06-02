import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Wait for backend to be ready
for attempt in range(5):
    stdin, stdout, stderr = client.exec_command('docker logs hartbeat-backend --tail 3 2>&1 | grep -i "daphne\|start\|listening\|Starting"')
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'Starting Daphne' in out or 'daphne' in out:
        print(f"Backend ready after {attempt*3}s")
        break
    print(f"Waiting... (attempt {attempt+1})")
    time.sleep(3)
    client.close()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test media
stdin, stdout, stderr = client.exec_command('curl -s -o /dev/null -w "HTTP:%{http_code}" http://localhost:8005/media/avatars/Screenshot_2026-04-21_201547.png 2>/dev/null')
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Media file: {out}")

stdin, stdout, stderr = client.exec_command('curl -s -o /dev/null -w "HTTP:%{http_code}" http://localhost:8005/admin/login/ 2>/dev/null')
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Admin login: {out}")

client.close()

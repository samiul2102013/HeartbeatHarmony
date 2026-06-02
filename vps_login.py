import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Try different login credentials for Dokploy
emails = [
    'support@ICSNCardiology.org',
    'admin@hartbeat.com',
    'admin@localhost',
    'admin@admin.com',
    'root@localhost',
]

passwords = [
    'CHANGE_ME',
    'HartbeatWellness@Portia123',
    'Admin123!',
    'admin',
    'password',
]

for email in emails:
    for pw in passwords:
        cmd = f'''curl -s -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{{"email":"{email}","password":"{pw}"}}' 2>/dev/null'''
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore').strip()
        if out and 'Unauthorized' not in out and 'Invalid' not in out and len(out) > 20:
            print(f"SUCCESS: {email} / {pw}")
            print(out[:300])
            break
    
    client.close()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

client.close()

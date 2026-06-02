import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'curl -s -o /dev/null -w "HTTP:%{http_code} SIZE:%{size_download}" http://localhost:8005/media/avatars/Screenshot_2026-04-21_201547.png 2>/dev/null',
    'curl -s -o /dev/null -w "HTTP:%{http_code}" http://localhost:8005/static/admin/css/base.css 2>/dev/null',
    'curl -s -o /dev/null -w "HTTP:%{http_code}" http://localhost:8005/admin/login/ 2>/dev/null',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {i+1} ===")
    print(out[:300] if out else "(empty)")
    print()

client.close()

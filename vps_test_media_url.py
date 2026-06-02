import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Test specific media file
    'curl -s -o /dev/null -w "HTTP:%{http_code} SIZE:%{size_download}" http://localhost:8005/media/avatars/Screenshot_2026-04-21_201547.png 2>/dev/null',
    # Test static file
    'curl -s -o /dev/null -w "HTTP:%{http_code} SIZE:%{size_download}" http://localhost:8005/static/admin/css/base.css 2>/dev/null',
    # Check Content-Type for media file
    'curl -s -D - http://localhost:8005/media/avatars/Screenshot_2026-04-21_201547.png 2>/dev/null | head -10',
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

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check if media volume exists
    'docker volume ls | grep media',
    # Check media directory inside backend container
    'docker exec hartbeat-backend ls -la /app/media/ 2>/dev/null',
    'docker exec hartbeat-backend find /app/media -type f 2>/dev/null | head -20',
    # Check static files
    'docker exec hartbeat-backend ls -la /app/staticfiles/ 2>/dev/null | head -10',
    # Test serving a media file (if any exist)
    'docker exec hartbeat-backend sh -c "ls /app/media/ 2>/dev/null && echo MEDIA_OK || echo NO_MEDIA"',
    # Check if avatars directory has files
    'docker exec hartbeat-backend ls -la /app/media/avatars/ 2>/dev/null || echo NO_AVATARS',
    # Test media URL response
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/media/ 2>/dev/null',
    # Check total disk usage of media
    'docker exec hartbeat-backend du -sh /app/media/ 2>/dev/null || echo NO_MEDIA_DIR',
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

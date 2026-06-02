import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Write script to host, copy to container, run via manage.py shell
script = "from apps.accounts.models import User; u=User.objects.create_user(username='support@ICSNCardiology.org', email='support@ICSNCardiology.org', password='Admin@123456', role='admin', is_active=True, email_verified=True); print(f'Created: {u.email} role={u.role}')"

# Use heredoc approach
cmds = [
    "docker cp /tmp/create_admin.py hartbeat-backend:/tmp/create_admin.py 2>/dev/null; echo ok",
    f'docker exec hartbeat-backend sh -c "cd /app && python manage.py shell << ENDSCRIPT\n{script}\nENDSCRIPT" 2>&1',
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(out[:500] if out else "done")
    if err: print(f"ERR: {err[:300]}")

client.close()

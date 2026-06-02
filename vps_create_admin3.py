import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Write a Python script to the container and execute
script = 'from apps.accounts.models import User; u=User.objects.create_user(username="support@ICSNCardiology.org", email="support@ICSNCardiology.org", password="Admin@123456", role="admin", is_active=True, email_verified=True); print(f"Created: {u.email} role={u.role} active={u.is_active} verified={u.email_verified}")'

cmd = f'docker exec hartbeat-backend sh -c "echo \'{script}\' | python manage.py shell" 2>&1'
stdin, stdout, stderr = client.exec_command(cmd)
print("OUT:", stdout.read().decode().strip())
err = stderr.read().decode().strip()
if err: print("ERR:", err[:500])

client.close()

import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Write script to VPS
script_content = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.accounts.models import User
u = User.objects.create_user(
    username='support@ICSNCardiology.org',
    email='support@ICSNCardiology.org',
    password='Admin@123456',
    role='admin',
    is_active=True,
    email_verified=True
)
print(f'Created: {u.email} role={u.role} active={u.is_active} verified={u.email_verified}')
"""

sftp = client.open_sftp()
with sftp.open('/tmp/create_admin.py', 'w') as f:
    f.write(script_content)
sftp.close()

# Execute it inside the container
stdin, stdout, stderr = client.exec_command("docker cp /tmp/create_admin.py hartbeat-backend:/tmp/create_admin.py && docker exec hartbeat-backend python /tmp/create_admin.py 2>&1")
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("OUT:", out)
if err: print("ERR:", err)

client.close()

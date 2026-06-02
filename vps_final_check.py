import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = '''from apps.accounts.models import User
from django.db import connection
print("=== DB CONNECTION ===")
print("DB Vendor:", connection.vendor)
print("=== USERS IN DB ===")
users = list(User.objects.all())
print(f"Total users: {len(users)}")
for u in users:
    print(f"Email: {u.email} | Role: {u.role} | Active: {u.is_active} | Verified: {u.email_verified}")
'''

# Write script to VPS
sftp = c.open_sftp()
with sftp.open('/tmp/check_users.py', 'w') as f:
    f.write(script)
sftp.close()

# Execute in container
stdin, stdout, stderr = c.exec_command("docker cp /tmp/check_users.py hartbeat-backend:/tmp/check_users.py && docker exec hartbeat-backend bash -c 'cd /app && python /tmp/check_users.py' 2>&1")
out = stdout.read().decode()
err = stderr.read().decode()
print("OUTPUT:")
print(out)
if err:
    print("ERROR:", err)

c.close()
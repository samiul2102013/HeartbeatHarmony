import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Write a simple check script
check_script = '''
from django.db import connection
from apps.accounts.models import User
print("=== DATABASE CHECK ===")
print("Tables:", list(connection.introspection.table_names()))
print("=== USERS ===")
users = list(User.objects.all())
print(f"Count: {len(users)}")
for u in users[:5]:  # Show first 5
    print(f"  {u.email} role={u.role} active={u.is_active} verified={u.email_verified}")
'''

# Write script to VPS and execute via container
sftp = c.open_sftp()
with sftp.open('/tmp/check_db.py', 'w') as f:
    f.write(check_script)
sftp.close()

# Execute in container
stdin, stdout, stderr = c.exec_command("docker cp /tmp/check_db.py hartbeat-backend:/tmp/check_db.py && docker exec hartbeat-backend python /tmp/check_db.py 2>&1")
out = stdout.read().decode()
err = stderr.read().decode()
print("OUTPUT:")
print(out)
if err:
    print("ERROR:", err)

c.close()
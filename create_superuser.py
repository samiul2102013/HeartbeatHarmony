import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Create a simple Python script to create superuser
script = '''from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'support@ICSNCardiology.org', 'Admin@123456')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
'''

# Write script to VPS
sftp = c.open_sftp()
with sftp.open('/tmp/create_superuser.py', 'w') as f:
    f.write(script)
sftp.close()

# Execute in container
stdin, stdout, stderr = c.exec_command("docker cp /tmp/create_superuser.py hartbeat-backend:/tmp/create_superuser.py && docker exec hartbeat-backend python /tmp/create_superuser.py 2>&1")
out = stdout.read().decode()
err = stderr.read().decode()
print("OUTPUT:")
print(out)
if err:
    print("ERROR:", err)

c.close()
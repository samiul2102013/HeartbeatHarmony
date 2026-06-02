import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = '''from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'support@ICSNCardiology.org',
        'role': 'admin',
        'is_active': True,
        'email_verified': True,
        'is_superuser': True,
        'is_staff': True,
    }
)
if created:
    u.set_password('Admin@123456')
    u.save()
    print(f'Created admin: {u.email} role={u.role}')
else:
    u.role = 'admin'
    u.set_password('Admin@123456')
    u.save()
    print(f'Updated admin: {u.email} role={u.role}')
'''

sftp = c.open_sftp()
with sftp.open('/tmp/create_admin.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/create_admin.py hartbeat-backend:/tmp/create_admin.py && docker exec hartbeat-backend bash -c 'cd /app && python /tmp/create_admin.py' 2>&1")
print(stdout.read().decode()[:500])
c.close()

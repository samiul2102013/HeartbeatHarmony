import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = '''from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(email__iexact='support@ICSNCardiology.org')
u.email = u.email.lower()
u.save()
print(f'Fixed email: {u.email} role={u.role}')
'''

sftp = c.open_sftp()
with sftp.open('/tmp/fix_email.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/fix_email.py hartbeat-backend:/tmp/fix_email.py && docker exec hartbeat-backend bash -c 'cd /app && cat /tmp/fix_email.py | python manage.py shell' 2>&1")
print(stdout.read().decode()[:500])
c.close()

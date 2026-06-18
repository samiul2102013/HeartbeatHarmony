import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

cmd = "docker exec hartbeat-backend python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(email='support@icsncardiology.org'); print(f'id={u.id}, email={u.email}, is_staff={u.is_staff}, is_superuser={u.is_superuser}, is_active={u.is_active}'); print(f'check pass Admin@123456: {u.check_password(\\\"Admin@123456\\\")}'); print(f'check pass admin123: {u.check_password(\\\"admin123\\\")}')\""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print('STDERR:', err)

client.close()

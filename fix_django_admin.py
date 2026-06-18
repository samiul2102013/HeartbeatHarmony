import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

cmd = "docker exec hartbeat-backend python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(email='support@ICSNCardiology.org'); u.is_staff = True; u.is_superuser = True; u.save(); print(f'Updated: {u.email} is_staff={u.is_staff} is_superuser={u.is_superuser}')\""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print('STDERR:', err)

client.close()

import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.core.models import ContentPage
p = ContentPage.objects.get(slug='account-deletion-policy')
print(repr(p.content))
print('---')
print(p.content[:300])
" """

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print('ERR:', err)
client.close()

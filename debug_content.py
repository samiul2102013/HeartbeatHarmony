import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

# Check what content is currently in the backend DB
cmd = """docker exec hartbeat-backend python manage.py shell -c "
from apps.core.models import ContentPage
for p in ContentPage.objects.filter(slug__in=['account-deletion-policy', 'privacy-policy', 'terms-of-service']):
    print(f'{p.slug}: title={p.title}, content_len={len(p.content)}')
" """

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print('ERR:', err)
client.close()

import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

cmd = """docker exec hartbeat-backend python manage.py shell -c "
import html
from apps.core.models import ContentPage

for p in ContentPage.objects.all():
    old = p.content
    unescaped = html.unescape(old)
    if unescaped != old:
        p.content = unescaped
        p.save(update_fields=['content'])
        print(f'Fixed: {p.slug} ({len(old)} -> {len(unescaped)})')
    else:
        print(f'OK: {p.slug}')
" """

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print('ERR:', err)
client.close()

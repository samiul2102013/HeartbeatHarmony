import paramiko
import sys

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

cmd = 'docker compose -f /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code/docker-compose.dokploy.yml exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); print(list(User.objects.values_list(\"id\",\"email\",\"username\")))"'

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS)
stdin, stdout, stderr = c.exec_command(cmd)
sys.stdout.write(stdout.read().decode('utf-8', errors='replace'))
sys.stderr.write(stderr.read().decode('utf-8', errors='replace'))
c.close()

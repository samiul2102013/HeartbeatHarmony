import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

cmd = "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && git fetch --force origin && git reset --hard origin/main && docker compose -f docker-compose.dokploy.yml build frontend 2>&1 | tail -5 && docker compose -f docker-compose.dokploy.yml up -d frontend"

print("Deploying...")
stdin, stdout, stderr = client.exec_command(cmd)
exit_status = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
for line in (out + err).split('\n')[-15:]:
    if line.strip():
        print(line.encode('ascii', errors='replace').decode('ascii'))
print("Done!")
client.close()

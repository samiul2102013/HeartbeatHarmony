import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

# Restart backend to pick up new URL
cmd = "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d backend"
print("Restarting backend...")
stdin, stdout, stderr = client.exec_command(cmd)
exit_status = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
if out:
    for line in out.split('\n')[-5:]:
        print(line.encode('ascii', errors='replace').decode('ascii'))
if err:
    for line in err.split('\n')[-5:]:
        print('ERR:', line.encode('ascii', errors='replace').decode('ascii'))
print("Done!")
client.close()

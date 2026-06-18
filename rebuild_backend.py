import paramiko

HOST = '2.24.115.93'
USER = 'root'
PASS = 'HartbeatWellness@Portia123'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS)

commands = [
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml build backend 2>&1 | tail -10",
    "cd /etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code && docker compose -f docker-compose.dokploy.yml up -d backend",
]

for cmd in commands:
    print(f"Running: {cmd[:60]}...")
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        for line in out.split('\n')[-10:]:
            print(line.encode('ascii', errors='replace').decode('ascii'))
    if err:
        for line in err.split('\n')[-5:]:
            print('ERR:', line.encode('ascii', errors='replace').decode('ascii'))
    print()

print("Done!")
client.close()

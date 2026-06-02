import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Stop and disable host PostgreSQL before Docker postgres starts
cmds = [
    'systemctl stop postgresql',
    'systemctl disable postgresql',
    'systemctl is-active postgresql',
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"{out}")
    if err: print(f"ERR: {err}")

client.close()

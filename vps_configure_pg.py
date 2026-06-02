import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Configure postgresql.conf to listen on all interfaces
cmd1 = "sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" /etc/postgresql/16/main/postgresql.conf"
# Configure pg_hba.conf - add docker subnet access
cmd2 = """echo "host    all             all             10.0.1.0/24            md5
host    all             all             172.17.0.0/16          md5
host    all             all             172.18.0.0/16          md5
host    all             all             172.19.0.0/16          md5
host    all             all             127.0.0.1/32           md5" >> /etc/postgresql/16/main/pg_hba.conf"""
# Restart postgresql
cmd3 = "systemctl restart postgresql && systemctl is-active postgresql"

for cmd in [cmd1, cmd2, cmd3]:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"RESULT: {out}")
    if err: print(f"ERR: {err}")

# Verify PostgreSQL is listening
stdin, stdout, stderr = client.exec_command("ss -tlnp | grep 5432")
print(f"\nListening: {stdout.read().decode().strip()}")

client.close()

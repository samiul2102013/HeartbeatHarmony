import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Create database and user
commands = [
    r"sudo -u postgres psql -c \"CREATE USER hartbeat WITH PASSWORD 'HartbeatDB@2026';\" 2>&1",
    r"sudo -u postgres psql -c \"CREATE DATABASE hartbeat_db OWNER hartbeat;\" 2>&1",
    r"sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE hartbeat_db TO hartbeat;\" 2>&1",
    r"sudo -u postgres psql -c \"ALTER DATABASE hartbeat_db OWNER TO hartbeat;\" 2>&1",
    r"sudo -u postgres psql -d hartbeat_db -c \"GRANT ALL ON SCHEMA public TO hartbeat;\" 2>&1",
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"CMD: {cmd[:50]}...")
    print(f"  OUT: {out}")
    if err: print(f"  ERR: {err}")

# Find PostgreSQL config files
stdin, stdout, stderr = client.exec_command("ls /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/postgresql.conf 2>&1")
print(f"\nConfig files: {stdout.read().decode().strip()}")

client.close()

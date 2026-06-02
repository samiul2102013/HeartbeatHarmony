import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Create SQL file on server
sql = """CREATE USER hartbeat WITH PASSWORD 'HartbeatDB@2026';
CREATE DATABASE hartbeat_db OWNER hartbeat;
GRANT ALL PRIVILEGES ON DATABASE hartbeat_db TO hartbeat;
\\c hartbeat_db
GRANT ALL ON SCHEMA public TO hartbeat;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hartbeat;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hartbeat;
"""

stdin, stdout, stderr = client.exec_command("cat > /tmp/setup.sql << 'EOF'\n" + sql + "\nEOF")
out = stdout.read().decode()
err = stderr.read().decode()
print("Write file:", out[:200] if out else "ok")
if err: print(f"ERR: {err[:200]}")

# Execute SQL
stdin, stdout, stderr = client.exec_command("sudo -u postgres psql -f /tmp/setup.sql 2>&1")
print(stdout.read().decode()[:1000])
err = stderr.read().decode()
if err: print(f"ERR: {err[:500]}")

client.close()

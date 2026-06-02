import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check postgres volumes
stdin, stdout, stderr = c.exec_command("docker volume ls | grep postgres")
print("Volumes:", stdout.read().decode())

# Check if postgres is running and has data
stdin, stdout, stderr = c.exec_command("docker ps --filter name=hartbeat-postgres --format '{{.Names}} {{.Status}}'")
print("Postgres:", stdout.read().decode())

# Try to query the database
stdin, stdout, stderr = c.exec_command("docker exec hartbeat-postgres psql -U hartbeat -d hartbeat_db -c 'SELECT email, role FROM users;' 2>&1")
out = stdout.read().decode()
print("Users in DB:", out[:500] if out else "(empty)")
c.close()

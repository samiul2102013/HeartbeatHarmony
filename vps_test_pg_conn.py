import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test connection from inside the backend container
# First, find the gateway IP that works
cmd = "docker exec hartbeat-backend sh -c 'apt-get update -qq && apt-get install -y -qq postgresql-client 2>&1 | tail -3'"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode()[:300])

# Now test the connection
cmd2 = "docker exec hartbeat-backend psql 'postgresql://hartbeat:HartbeatDB@2026@172.18.0.1:5432/hartbeat_db' -c 'SELECT 1 as test;' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd2)
print(f"\nTest (172.18.0.1): {stdout.read().decode().strip()[:200]}")
err = stderr.read().decode().strip()
if err: print(f"ERR: {err[:200]}")

# Try with host's IP
cmd3 = "docker exec hartbeat-backend psql 'postgresql://hartbeat:HartbeatDB@2026@2.24.115.93:5432/hartbeat_db' -c 'SELECT 1 as test;' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd3)
print(f"Test (2.24.115.93): {stdout.read().decode().strip()[:200]}")
err = stderr.read().decode().strip()
if err: print(f"ERR: {err[:200]}")

# Try with dokploy gateway
cmd4 = "docker exec hartbeat-backend psql 'postgresql://hartbeat:HartbeatDB@2026@10.0.1.1:5432/hartbeat_db' -c 'SELECT 1 as test;' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd4)
print(f"Test (10.0.1.1): {stdout.read().decode().strip()[:200]}")
err = stderr.read().decode().strip()
if err: print(f"ERR: {err[:200]}")

client.close()

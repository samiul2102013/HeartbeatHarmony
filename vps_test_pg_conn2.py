import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Test with URL-encoded password (the @ becomes %40)
cmds = [
    "docker exec hartbeat-backend psql 'postgresql://hartbeat:HartbeatDB%402026@172.18.0.1:5432/hartbeat_db' -c 'SELECT 1 as test;'",
    "docker exec hartbeat-backend psql 'postgresql://hartbeat:HartbeatDB%402026@127.0.0.1:5432/hartbeat_db' -c 'SELECT 1 as test;'",
]

for cmd in cmds:
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"CMD: {cmd[:70]}...")
    print(f"  OUT: {out[:300]}")
    if err: print(f"  ERR: {err[:300]}")

c.close()

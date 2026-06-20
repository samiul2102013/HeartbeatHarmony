import paramiko
host, user, password = '2.24.115.93', 'root', 'HartbeatWellness@Portia123'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password, timeout=10)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out: print(out)
    if err: print("ERR:", err[:500])
    return out

print("=== Pull latest ===")
run("cd ~/hartbeat-harmony && git pull", 30)

print("\n=== Rebuild frontend ===")
run("cd ~/hartbeat-harmony && docker compose --env-file .env.dokploy -f docker-compose.dokploy.yml build frontend 2>&1 | tail -5", 300)

print("\n=== Remove old frontend container ===")
run("docker rm -f hartbeat-frontend 2>/dev/null; echo removed", 15)

print("\n=== Start new frontend ===")
run("cd ~/hartbeat-harmony && docker compose --env-file .env.dokploy -f docker-compose.dokploy.yml up -d --no-deps frontend 2>&1", 60)

print("\n=== Status ===")
run("docker ps --filter name=hartbeat --format '{{.Names}} {{.Status}}'", 10)

client.close()

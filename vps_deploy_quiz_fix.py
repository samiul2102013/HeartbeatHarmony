import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

def run(cmd, timeout=300):
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    if out:
        print(out)
    if err:
        print(f"[ERR] {err}")
    return out, err

# Step 1: Pull latest code from git
run('cd /root/hartbeat-harmony && git pull origin main', timeout=120)

# Step 2: Rebuild frontend, backend, and nginx (nginx config body size changed)
run(
    'cd /root/hartbeat-harmony && '
    'docker compose -p hartbeatstack-hartbeatstack-buv5uf -f docker-compose.dokploy.yml --env-file .env.dokploy '
    'build --no-cache frontend backend nginx',
    timeout=600
)

# Step 3: Restart the updated containers
run(
    'cd /root/hartbeat-harmony && '
    'docker compose -p hartbeatstack-hartbeatstack-buv5uf -f docker-compose.dokploy.yml --env-file .env.dokploy '
    'up -d frontend backend nginx',
    timeout=120
)

# Step 4: Verify containers are running
time.sleep(5)
run('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep hartbeat')

client.close()
print("\nDeploy complete!")

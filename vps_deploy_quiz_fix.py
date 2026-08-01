import paramiko
import time
import sys

# Fix Unicode output on Windows console
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

def run(cmd, timeout=300):
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"[ERR] {err}")
    return out, err

# Step 1: Stash any local VPS changes, then pull
run('cd /root/hartbeat-harmony && git stash', timeout=30)
run('cd /root/hartbeat-harmony && git pull origin main', timeout=120)

# Step 2: Rebuild nginx (video streaming config changes), frontend, backend
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
run('docker ps --format "table {{.Names}}\t{{.Status}}" | grep hartbeat')

client.close()
print("\nDeploy complete!")

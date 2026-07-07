import paramiko
import time
import sys

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

command = " && ".join([
    "cd /root/hartbeat-harmony",
    "echo '=== GIT FETCH ==='",
    "git fetch origin",
    "echo '=== GIT RESET ==='",
    "git reset --hard origin/main",
    "echo '=== DOCKER BUILD ==='",
    "docker compose --env-file .env.dokploy -f docker-compose.dokploy.yml build backend 2>&1",
    "echo '=== DOCKER UP ==='",
    "docker rm -f hartbeat-backend 2>/dev/null; docker compose --env-file .env.dokploy -f docker-compose.dokploy.yml up -d --no-deps backend 2>&1",
    "echo '=== DONE ==='",
])

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting...")
    client.connect(host, username=username, password=password, timeout=15, banner_timeout=30)
    print("Connected. Running deployment...\n")

    channel = client.get_transport().open_session()
    channel.exec_command(command)
    channel.settimeout(600)

    start = time.time()
    while True:
        if channel.recv_ready():
            data = channel.recv(4096).decode("utf-8", errors="replace")
            sys.stdout.write(data)
            sys.stdout.flush()
        elif channel.recv_stderr_ready():
            data = channel.recv_stderr(4096).decode("utf-8", errors="replace")
            sys.stdout.write(data)
            sys.stdout.flush()
        elif channel.exit_status_ready():
            break
        elapsed = time.time() - start
        if elapsed > 590:
            print(f"\nTimeout after {elapsed:.0f}s")
            channel.close()
            break
        time.sleep(0.5)

    exit_code = channel.recv_exit_status()
    print(f"\nExit code: {exit_code}")
    print("Deployment completed" if exit_code == 0 else "Deployment failed")

except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()

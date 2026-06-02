import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Restart Traefik to force ACME certificate renewal for all domains
stdin, stdout, stderr = client.exec_command('docker restart dokploy-traefik')
print("Restart result:", stdout.read().decode().strip())
print("Errors:", stderr.read().decode().strip())

# Wait a bit and check logs
import time
time.sleep(10)

# Check if ACME is now being processed for admin
stdin, stdout, stderr = client.exec_command("docker logs dokploy-traefik --tail 20 2>&1 | grep -i 'admin\.heartbeat\|acme\|certif'")
print("\nACME logs after restart:")
print(stdout.read().decode().strip()[:2000])

# Wait more and check again
time.sleep(30)

stdin, stdout, stderr = client.exec_command(r"docker logs dokploy-traefik --tail 30 2>&1")
all_logs = stdout.read().decode().strip()
# Filter for relevant lines
for line in all_logs.split('\n'):
    if any(x in line.lower() for x in ['acme', 'certif', 'admin', 'challenge']):
        print(line)

client.close()

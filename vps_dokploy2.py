import paramiko, sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Get docker logs without emojis
stdin, stdout, stderr = client.exec_command('docker service logs dokploy --tail 30 2>/dev/null || docker logs $(docker ps --format "{{.Names}}" | grep "dokploy.1" | head -1) 2>&1 | tail -30')
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(out[:2000])
print("---")

# Check Traefik config
stdin, stdout, stderr = client.exec_command('docker config ls 2>/dev/null; echo "==="; docker container inspect dokploy-traefik --format "{{range .Config.Env}}{{println .}}{{end}}" 2>/dev/null | head -20')
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(out[:2000])

client.close()

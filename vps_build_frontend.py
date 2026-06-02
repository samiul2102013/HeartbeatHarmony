import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Build frontend
cmd = 'cd /root/hartbeat-harmony && docker compose -f docker-compose.dokploy.yml --env-file .env.dokploy build frontend 2>&1 | tail -40'
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== FRONTEND BUILD ===")
print(out[-3000:] if len(out) > 3000 else out)
if err:
    print(f"[ERR] {err[:500]}")

client.close()

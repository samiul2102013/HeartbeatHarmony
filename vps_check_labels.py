import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = client.exec_command('docker inspect hartbeat-frontend --format "{{json .Config.Labels}}" 2>/dev/null')
frontend_labels = json.loads(stdout.read().decode('utf-8', errors='ignore'))

stdin, stdout, stderr = client.exec_command('docker inspect hartbeat-backend --format "{{json .Config.Labels}}" 2>/dev/null')
backend_labels = json.loads(stdout.read().decode('utf-8', errors='ignore'))

print("=== FRONTEND LABELS ===")
for k, v in sorted(frontend_labels.items()):
    if 'traefik' in k:
        print(f"  {k}={v}")

print("\n=== BACKEND LABELS ===")
for k, v in sorted(backend_labels.items()):
    if 'traefik' in k:
        print(f"  {k}={v}")

client.close()

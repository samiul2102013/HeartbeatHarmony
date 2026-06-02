import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = client.exec_command("docker inspect hartbeat-frontend --format '{{json .Config.Labels}}'")
raw = stdout.read().decode('utf-8', errors='ignore')
labels = json.loads(raw)
for k, v in sorted(labels.items()):
    if 'service' in k.lower() or 'frontend' in k.lower() or 'router' in k.lower():
        print(f"  {k}={v}")
client.close()

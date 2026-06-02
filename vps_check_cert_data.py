import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check ACME cert validity directly from acme.json
cmd = "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>&1"
stdin, stdout, stderr = client.exec_command(cmd)
import json
data = json.loads(stdout.read().decode())
certs = data.get('letsencrypt', {}).get('Certificates', [])
for c in certs:
    domain = c.get('domain', {}).get('main', '?')
    cert = c.get('certificate', '')
    key = c.get('key', '')
    store = c.get('store', '?')
    cert_len = len(cert) if cert else 0
    key_len = len(key) if key else 0
    print(f"Domain: {domain}")
    print(f"  Certificate length: {cert_len}")
    print(f"  Key length: {key_len}")
    print(f"  Store: {store}")
    print()

client.close()

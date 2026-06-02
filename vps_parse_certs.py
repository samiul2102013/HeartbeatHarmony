import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = client.exec_command("docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json")
data = json.loads(stdout.read().decode('utf-8', errors='ignore'))
client.close()

# Print certificates
certs = data.get('letsencrypt', {}).get('Certificates', [])
if certs:
    print(f"Found {len(certs)} certificate(s):")
    for c in certs:
        print(f"  Main: {c.get('domain', {}).get('main', '?')}")
        sans = c.get('domain', {}).get('sans', [])
        if sans:
            print(f"  SANs: {sans}")
        print(f"  Store: {c.get('store', '?')}")
        print()
else:
    print("No Certificates found in acme.json")
    
# Also show account info
acct = data.get('letsencrypt', {}).get('Account', {})
print(f"Account status: {acct.get('Registration', {}).get('body', {}).get('status', 'unknown')}")
print(f"Account URI: {acct.get('Registration', {}).get('uri', 'unknown')}")

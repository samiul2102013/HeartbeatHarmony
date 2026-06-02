import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check current Traefik logs - newest first
stdin, stdout, stderr = client.exec_command("docker logs dokploy-traefik --tail 30 2>&1 | tail -10")
print("=== NEWEST TRAEFIK LOGS ===")
print(stdout.read().decode()[:2000])

# Check cert from inside VPS
stdin, stdout, stderr = client.exec_command("curl -sI https://admin.heartbeatharmony.tech 2>&1 | head -10 || echo 'curl failed'")
print("\n=== HTTPS RESPONSE HEADERS ===")
print(stdout.read().decode()[:1000])

# Check what cert is being served using openssl
stdin, stdout, stderr = client.exec_command("echo | openssl s_client -connect admin.heartbeatharmony.tech:443 -servername admin.heartbeatharmony.tech 2>&1 | openssl x509 -noout -subject -issuer -dates 2>&1 | head -10")
print("\n=== SSL CERT INFO ===")
print(stdout.read().decode()[:1000])

client.close()

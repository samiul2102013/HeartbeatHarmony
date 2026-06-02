import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check if openssl is available for direct cert check
stdin, stdout, stderr = client.exec_command("which openssl && echo | openssl s_client -connect 127.0.0.1:443 -servername admin.heartbeatharmony.tech 2>&1 | openssl x509 -noout -subject -issuer -dates 2>&1 || echo 'openssl not available'")
out = stdout.read().decode('utf-8', errors='ignore')
print(out[:2000])

# Check cert store inside Traefik - there's a certs endpoint
stdin, stdout, stderr = client.exec_command("docker exec dokploy-traefik wget -qO- http://localhost:8080/api/overview 2>&1 | head -c 200")
out2 = stdout.read().decode('utf-8', errors='ignore')
print(f"\nAPI overview:\n{out2[:500] if out2 else '(empty)'}")

client.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Test basic API connectivity
    'curl -v http://localhost:3000/api/health 2>&1 | head -20',
    # Check API response for any endpoint
    'curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:3000/api/auth/register 2>&1',
    # Try GET request
    'curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:3000/api/project 2>&1',
    # Read the auth secret
    'cat /run/secrets/dokploy_auth_secret 2>/dev/null || docker exec $(docker ps --format "{{.Names}}" | grep dokploy.1 | head -1) cat /run/secrets/dokploy_auth_secret 2>/dev/null',
    # Read postgres password
    'docker exec $(docker ps --format "{{.Names}}" | grep dokploy.1 | head -1) cat /run/secrets/postgres_password 2>/dev/null',
    # Check dokploy database for users
    'docker exec $(docker ps --format "{{.Names}}" | grep dokploy.1 | head -1) sh -c "psql -U postgres -d dokploy -c \"SELECT email, name, role FROM \\\"User\\\" LIMIT 5;\" 2>/dev/null"',
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== CMD {i+1} ===")
    print(out[:1500] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

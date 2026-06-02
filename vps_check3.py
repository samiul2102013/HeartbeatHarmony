import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Save output to file on VPS to avoid encoding issues
cmd = '''docker service logs dokploy --tail 50 2>/dev/null | tr -dc '[:print:]\\n\\t' > /tmp/dokploy_logs.txt 2>/dev/null; cat /tmp/dokploy_logs.txt | grep -i "admin\|email\|password\|register\|setup\|token\|secret" | head -20'''
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print("Dokploy logs (admin related):")
print(out[:2000] if out else "No matches found")
print("===")

# Check if there's a Dokploy initial setup page
cmd2 = "curl -s http://localhost:3000/api/auth/status 2>/dev/null || curl -s http://localhost:3000/api/health 2>/dev/null || echo NONE"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Dokploy auth status: {out[:500]}")
print("===")

# Check if there's a registered admin
cmd3 = "docker exec $(docker ps --format '{{.Names}}' | grep dokploy.1 | head -1) sh -c 'psql $DATABASE_URL -c \"SELECT email FROM User\" 2>/dev/null || echo DB_QUERY_FAILED'"
stdin, stdout, stderr = client.exec_command(cmd3)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Dokploy users: {out[:500]}")

client.close()

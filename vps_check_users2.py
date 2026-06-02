import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Write a Python script to VPS and execute it
script = """from apps.accounts.models import User
print(f'Total users: {User.objects.count()}')
for u in User.objects.all().order_by('-id')[:5]:
    print(f'ID={u.id}, Email={u.email[:30]}, Username={u.username}, Role={u.role}')
"""

# Save script to VPS
cmd1 = f"cat > /tmp/check_users.py << 'SCRIPTEOF'\n{script}\nSCRIPTEOF"
stdin, stdout, stderr = client.exec_command(cmd1)
err = stderr.read().decode('utf-8', errors='ignore').strip()
print(f"Script saved: {err if err else 'OK'}")

# Execute it
cmd2 = "docker cp /tmp/check_users.py hartbeat-backend:/tmp/ && docker exec hartbeat-backend python /tmp/check_users.py"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
err = stderr.read().decode('utf-8', errors='ignore').strip()
print("=== Users (last 5) ===")
print(out[:1000] if out else "(empty)")
if err:
    print(f"[ERR] {err[:500]}")

client.close()

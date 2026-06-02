import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = "docker exec hartbeat-backend python manage.py shell -c 'from apps.accounts.models import User; u=User.objects.create_user(email=\"support@ICSNCardiology.org\", password=\"Admin@123456\", role=\"admin\", is_verified=True, is_active=True); print(f\"Created: {u.email} role={u.role} verified={u.is_verified}\")' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("OUT:", out[:500])
if err: print("ERR:", err[:500])

# Verify login
cmd2 = "docker exec hartbeat-backend python manage.py shell -c 'from apps.accounts.models import User; u=User.objects.filter(email=\"support@ICSNCardiology.org\").first(); print(f\"Found: {u.email if u else \"NO USER\"} active={u.is_active if u else \"N/A\"} role={u.role if u else \"N/A\"}\")' 2>&1"
stdin, stdout, stderr = client.exec_command(cmd2)
out2 = stdout.read().decode().strip()
err2 = stderr.read().decode().strip()
print("Verify:", out2[:500])
if err2: print("ERR:", err2[:500])

client.close()

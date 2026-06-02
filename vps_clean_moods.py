import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# First delete the wrong nested files
cmd1 = "docker exec hartbeat-backend sh -c 'rm -rf /app/media/moods/svg/moods 2>/dev/null && echo CLEANED || echo NOTHING'"
stdin, stdout, stderr = client.exec_command(cmd1)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Cleanup: {out}")

# Check remaining files
cmd2 = "docker exec hartbeat-backend find /app/media/moods -type f 2>/dev/null"
stdin, stdout, stderr = client.exec_command(cmd2)
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(f"Remaining files: {out if out else '(empty)'}")

client.close()

import paramiko

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password, timeout=15)

# Look for the actual Python traceback for register 500
stdin, stdout, stderr = client.exec_command(
    'docker logs hartbeat-backend 2>&1 | grep -B2 -A30 "register.*500" | head -60',
    timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
print(out or "No output")
client.close()

import paramiko

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password, timeout=15)

stdin, stdout, stderr = client.exec_command(
    "docker ps --filter name=hartbeat --format '{{.Names}} {{.Status}}' && echo '---LOGS---' && docker logs hartbeat-backend --tail 50 2>&1",
    timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
print(out[:3000])
client.close()

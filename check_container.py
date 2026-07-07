import paramiko

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password, timeout=15)

cmds = [
    "docker ps --filter name=hartbeat --format '{{.Names}} {{.Status}}'",
    "docker logs hartbeat-backend --tail 30 2>&1",
]

for label, cmd in [("Container Status", cmds[0]), ("Backend Logs", cmds[1])]:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out[:2000])
    if err:
        print(f"ERR: {err[:500]}")

client.close()

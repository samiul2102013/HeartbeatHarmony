import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    "docker logs hartbeat-backend 2>&1 | grep -E -i 'email|smtp|mail|Sent|fail|error|Traceback' | head -20",
    "docker logs hartbeat-backend 2>&1 | tail -5",
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {i+1} ===")
    print(out[:1000] if out else "(no matching logs)")
    if err:
        print(f"[ERR] {err[:200]}")
    print()

client.close()

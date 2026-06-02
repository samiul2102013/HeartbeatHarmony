import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'curl -s http://localhost:3000/api/project 2>/dev/null || echo CURL_FAILED',
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/ 2>/dev/null",
    'docker network ls',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f"=== {cmd} ===")
    print(out if out else "(empty)")
    if err:
        print(f"[ERR] {err}")
    print()

client.close()

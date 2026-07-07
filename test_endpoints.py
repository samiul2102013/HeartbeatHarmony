import paramiko

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password, timeout=15)

cmds = [
    'curl -s -w "\\nHTTP_CODE:%{http_code}\\n" -X POST https://api.heartbeatharmony.tech/api/auth/apple/ -H "Content-Type: application/json" -d \'{"identity_token": "test"}\'',
    'curl -s -w "\\nHTTP_CODE:%{http_code}\\n" -X POST https://api.heartbeatharmony.tech/api/webhooks/app-store -H "Content-Type: application/json" -d \'{}\'',
    'curl -s -w "\\nHTTP_CODE:%{http_code}\\n" https://api.heartbeatharmony.tech/api/health/',
]

for label, cmd in [("Apple Login", cmds[0]), ("Apple Webhook", cmds[1]), ("Health", cmds[2])]:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out[:1500])
    if err:
        print(f"ERR: {err[:300]}")

client.close()
print("\nDone")

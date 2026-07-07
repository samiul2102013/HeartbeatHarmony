import paramiko

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password, timeout=15)

stdin, stdout, stderr = client.exec_command(
    'docker logs hartbeat-backend --tail 200 2>&1',
    timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")

# Find the last complete traceback before the HTTP status line
lines = out.split("\n")
capturing = False
traceback_lines = []
for i, line in enumerate(lines):
    if "Traceback (most recent call last)" in line:
        capturing = True
        traceback_lines = [line]
    elif capturing:
        traceback_lines.append(line)
        if line.startswith("10.") or line.startswith("jwt.") or "HTTP" in line:
            break

# Print the traceback
for l in traceback_lines:
    print(l)
client.close()

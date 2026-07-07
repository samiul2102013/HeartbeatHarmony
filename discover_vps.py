import paramiko

host = "2.24.115.93"
username = "root"
password = "HartbeatWellness@Portia123"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password, timeout=15)

commands = [
    "ls -la /root/hartbeat-harmony/",
    "cat /root/hartbeat-harmony/.git/config 2>/dev/null || echo 'no .git'",
    "ls -la /root/hartbeat-harmony/.git 2>/dev/null || echo 'no .git dir'",
    "git config --global --list 2>/dev/null",
]

for cmd in commands:
    print(f"\n$ {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out[:2000])
    if err:
        print(f"ERR: {err[:500]}")

client.close()

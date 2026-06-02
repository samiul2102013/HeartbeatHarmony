import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmds = [
    'docker ps --filter name=hartbeat --format "table {{.Names}}\t{{.Status}}"',
    'ls -la /root/hartbeat-harmony/.env.dokploy 2>/dev/null && cat /root/hartbeat-harmony/.env.dokploy || echo "no env file"',
]

for cmd in cmds:
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode()[:1500])
    print("---")
c.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'docker logs dokploy-traefik --tail 30 2>&1',
    'docker inspect hartbeat-frontend --format "{{.Config.Labels}}" 2>/dev/null | python -c "import sys,json; d=json.load(sys.stdin); [print(k,v) for k,v in sorted(d.items()) if \"service\" in k.lower()]" 2>/dev/null || echo no_python',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(out[:2000] if out else '(empty)')
    if err:
        print(f'ERR: {err[:300]}')
    print()

client.close()

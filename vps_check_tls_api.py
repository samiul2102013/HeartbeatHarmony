import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check Traefik certificate store
cmd1 = "docker exec dokploy-traefik wget -qO- http://localhost:8080/api/http 2>&1 | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2))' 2>&1 | head -200"
# Check TLS certs via API
cmd2 = "docker exec dokploy-traefik wget -qO- http://localhost:8080/api/tls 2>&1 | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2))' 2>&1 | head -200"

for cmd in [cmd1, cmd2]:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    if out and out != '{}':
        print(out[:2000])
    else:
        print("(empty)")
    if err:
        print(f'ERR: {err[:300]}')
    print()

client.close()

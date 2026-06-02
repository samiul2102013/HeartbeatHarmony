import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd1 = 'docker exec dokploy-traefik wget -qO- http://localhost:8080/api/http/routers 2>&1 | head -c 1000 || echo "API unavailable"'
cmd2 = "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>&1 | python3 -c 'import sys,json; d=json.load(sys.stdin); certs=d.get(\"letsencrypt\",{}).get(\"Certificates\",[]); [print(f\"Domain: {c.get(\\\"domain\\\",{}).get(\\\"main\\\",\\\"?\\\")}, Has cert: {bool(c.get(\\\"certificate\\\"))}\") for c in certs]' 2>&1 || echo 'no python3'"
cmd3 = 'docker logs dokploy-traefik --since 5m --tail 30 2>&1'

for cmd in [cmd1, cmd2, cmd3]:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(out[:2000] if out else '(empty)')
    if err:
        print(f'ERR: {err[:300]}')
    print()

client.close()

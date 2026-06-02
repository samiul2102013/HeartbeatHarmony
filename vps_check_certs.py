import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check Traefik certificates
commands = [
    # Check ACME json for certificates (the specific Domain part)
    "docker exec dokploy-traefik sh -c \"cat /etc/dokploy/traefik/dynamic/acme.json | python3 -c 'import sys,json; d=json.load(sys.stdin); certs=d.get(\\\"letsencrypt\\\",{}).get(\\\"Certificates\\\",[]); [print(c.get(\\\"domain\\\",{}).get(\\\"main\\\",\\\"?\\\")) for c in certs]' 2>/dev/null || echo NO_PYTHON\"",
    # Check if any certs exist for our domains
    "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/acme.json 2>/dev/null | grep -o '\"main\":\"[^\"]*\"' | head -10",
    # Check the Traefik dynamic config for our services
    "docker exec dokploy-traefik cat /etc/dokploy/traefik/dynamic/dokploy.yml 2>/dev/null | head -50",
    # Check if our services are in Traefik's dynamic config
    "docker exec dokploy-traefik ls /etc/dokploy/traefik/dynamic/ 2>/dev/null",
]

for i, cmd in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"=== {i+1} ===")
    print(out[:1500] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

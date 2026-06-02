import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check ACME errors for admin specifically
    r'docker logs dokploy-traefik --tail 100 2>&1 | grep -i "admin\.heartbeat\|acme\|certif\|challenge" | head -20',
    # Check Traefik health and cert status from API
    'docker exec dokploy-traefik wget -qO- http://localhost:8080/api/http/routers 2>/dev/null | python3 -c "import sys,json; data=json.load(sys.stdin); [print(r.get(\"name\",\"?\"), r.get(\"rule\",\"\"), r.get(\"tls\",{}).get(\"certResolver\",\"none\")) for r in data if \"admin\" in r.get(\"rule\",\"\") or \"api\" in r.get(\"rule\",\"\")]" 2>/dev/null || echo NO_API',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"CMD: {cmd[:80]}...")
    print(out[:2000] if out else "(empty)")
    if err:
        print(f"[ERR] {err[:300]}")
    print()

client.close()

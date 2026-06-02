import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

cmd = "docker exec dokploy-traefik wget -qO- http://localhost:8080/api/http/routers 2>&1 | python3 -c 'import sys,json; data=json.load(sys.stdin); [print(r.get(\"name\",\"?\"), r.get(\"rule\",\"\"), r.get(\"service\",\"\"), r.get(\"status\",\"\"), r.get(\"tls\",{}).get(\"certResolver\",\"none\")) for r in data if \"admin\" in r.get(\"rule\",\"\") or \"api\" in r.get(\"rule\",\"\")]'"

stdin, stdout, stderr = client.exec_command(cmd)
print("Routers for admin/api:")
print(stdout.read().decode()[:2000])
err = stderr.read().decode()
if err:
    print(f"ERR: {err[:500]}")

client.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Find the docker gateway IP for dokploy-network
cmds = [
    "docker network inspect dokploy-network --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}'",
    "docker network inspect dokploy-network --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'",
    "hostname -I",
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    print(f"{cmd.split()[0]}: {stdout.read().decode().strip()}")
    err = stderr.read().decode().strip()
    if err: print(f"  ERR: {err}")

client.close()

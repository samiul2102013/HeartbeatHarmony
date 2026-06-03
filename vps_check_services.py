import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Check what services are running
stdin, stdout, stderr = c.exec_command("docker service ls 2>&1")
out = stdout.read().decode()
print("Docker services:", out[:500])

stdin2, stdout2, stderr2 = c.exec_command("docker compose ls 2>&1")
out2 = stdout2.read().decode()
print("Compose projects:", out2[:500])

stdin3, stdout3, stderr3 = c.exec_command("ls /root/hartbeat-harmony/docker-compose* 2>&1")
out3 = stdout3.read().decode()
print("Compose files:", out3[:500])

c.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    'apt-get update -qq && apt-get install -y -qq postgresql postgresql-contrib 2>&1 | tail -5',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(out[:1000] if out else '(empty)')
    if err: print(f'ERR: {err[:300]}')

# Verify installation
import time
time.sleep(5)
stdin, stdout, stderr = client.exec_command('psql --version 2>&1')
print(f"\nVersion: {stdout.read().decode().strip()}")

client.close()

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

commands = [
    # Check if postgres is already installed
    'which psql 2>/dev/null && psql --version || echo "not_installed"',
    # Check available packages
    'apt list --installed 2>/dev/null | grep -i postgres',
    # Check disk space
    'df -h /',
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    print(f"CMD: {cmd[:80]}")
    print(out[:500] if out else '(empty)')
    if err: print(f'ERR: {err[:200]}')
    print()

client.close()

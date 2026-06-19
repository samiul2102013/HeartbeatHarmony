import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123',
          look_for_keys=False, allow_agent=False)

BASE = '/etc/dokploy/compose/hartbeatstack-hartbeatstack-buv5uf/code'
APPLE = '9691b16037ed4388a1cb063c62e65fc8'

# 1. Git reset to latest
i, o, e = c.exec_command('cd ' + BASE + ' && git fetch --force origin && git reset --hard origin/main')
print('Git:', o.read().decode().strip()[-100:])

# 2. Upload JSON file (git reset removes untracked files)
sftp = c.open_sftp()
with open('backend/resources/heartbeat-harmoney-8eff124fe434.json') as f:
    sa_info = json.load(f)
with sftp.open(BASE + '/google_service_account.json', 'w') as f:
    f.write(json.dumps(sa_info))
sftp.close()
print('JSON uploaded')

# 3. Build
i, o, e = c.exec_command(
    'cd ' + BASE + ' && APPLE_SHARED_SECRET=' + APPLE
    + ' docker compose -f docker-compose.dokploy.yml build backend 2>&1 | tail -3'
)
print('Build:', o.read().decode().strip())

# 4. Restart
i, o, e = c.exec_command(
    'cd ' + BASE + ' && APPLE_SHARED_SECRET=' + APPLE
    + ' docker compose -f docker-compose.dokploy.yml up -d backend 2>&1 | tail -5'
)
print('Deploy:', o.read().decode().strip())

# 5. Verify
i, o, e = c.exec_command('docker exec hartbeat-backend env | grep -E "APPLE|GOOGLE"')
for line in o.read().decode().split('\n'):
    if line.strip(): print('Env:', line)

i, o, e = c.exec_command('docker exec hartbeat-backend ls -la /app/google_service_account.json 2>&1')
print('File:', o.read().decode().strip())

c.close()
print('Done')

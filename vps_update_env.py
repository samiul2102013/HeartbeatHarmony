import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Update env with temporary IP-based values for testing
update_cmd = """cat > /root/hartbeat-harmony/.env.dokploy << 'ENVEOF'
API_DOMAIN=2.24.115.93
FRONTEND_DOMAIN=2.24.115.93
SECRET_KEY=4ibVkIkE5NceJBdJJOvACoK0okKPpGU-fPx7CBGlovCWFEyJmQYCJmy7359vm7vaCB8
DATABASE_URL=postgresql://neondb_owner:npg_2BFfoH0QCGJq@ep-nameless-wave-aopn0f19-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
DEFAULT_FROM_EMAIL=HeartBeat Harmony <support@ICSNCardiology.org>
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=support@ICSNCardiology.org
EMAIL_HOST_PASSWORD=CHANGE_ME
ENVEOF"""
stdin, stdout, stderr = client.exec_command(update_cmd)
err = stderr.read().decode('utf-8', errors='ignore').strip()
print(f"Env updated: {err if err else 'OK'}")
stdin, stdout, stderr = client.exec_command('cat /root/hartbeat-harmony/.env.dokploy | head -5')
print(stdout.read().decode('utf-8', errors='ignore').strip())

client.close()

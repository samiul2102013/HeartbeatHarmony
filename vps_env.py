import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Create production env file
content = """# Dokploy Production Environment
# Generated for Hartbeat Harmony deployment

API_DOMAIN=api.DOMAIN_HERE
FRONTEND_DOMAIN=admin.DOMAIN_HERE

# Django Secret Key
SECRET_KEY=4ibVkIkE5NceJBdJJOvACoK0okKPpGU-fPx7CBGlovCWFEyJmQYCJmy7359vm7vaCB8

# Database URL (keep existing Neon)
DATABASE_URL=postgresql://neondb_owner:npg_2BFfoH0QCGJq@ep-nameless-wave-aopn0f19-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

# SMTP (Hostinger)
DEFAULT_FROM_EMAIL=HeartBeat Harmony <support@ICSNCardiology.org>
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=support@ICSNCardiology.org
EMAIL_HOST_PASSWORD=CHANGE_ME
"""

# Write env file
cmd = f"cat > /root/hartbeat-harmony/.env.dokploy << 'ENVEOF'\n{content}\nENVEOF"
stdin, stdout, stderr = client.exec_command(cmd)
err = stderr.read().decode('utf-8', errors='replace').strip()
print(f"Env file created: {err if err else 'OK'}")

# Verify
stdin, stdout, stderr = client.exec_command('cat /root/hartbeat-harmony/.env.dokploy | head -30')
out = stdout.read().decode('utf-8', errors='replace').strip()
print(out)

client.close()

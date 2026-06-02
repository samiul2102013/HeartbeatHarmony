import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Create a production compose file that works without Traefik labels (direct port exposure)
compose_content = """services:
  redis:
    container_name: hartbeat-redis
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - hartbeat-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    container_name: hartbeat-backend
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8005:8005"
    environment:
      - DEBUG=False
      - SECRET_KEY=4ibVkIkE5NceJBdJJOvACoK0okKPpGU-fPx7CBGlovCWFEyJmQYCJmy7359vm7vaCB8
      - DATABASE_URL=postgresql://neondb_owner:npg_2BFfoH0QCGJq@ep-nameless-wave-aopn0f19-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
      - REDIS_URL=redis://hartbeat-redis:6379/0
      - ALLOWED_HOSTS=2.24.115.93,localhost,api.icsncardiology.org,admin.icsncardiology.org,.icsncardiology.org
      - CORS_ORIGINS=http://2.24.115.93:3004,http://localhost:3004,https://admin.icsncardiology.org,http://localhost:3000
      - CSRF_TRUSTED_ORIGINS=http://2.24.115.93:3004,http://2.24.115.93:8005,http://localhost:3004,http://localhost:3000,http://localhost:8005
      - FRONTEND_URL=http://2.24.115.93:3004
      - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
      - DEFAULT_FROM_EMAIL=HeartBeat Harmony <support@ICSNCardiology.org>
      - EMAIL_HOST=smtp.hostinger.com
      - EMAIL_PORT=587
      - EMAIL_USE_TLS=True
      - EMAIL_HOST_USER=support@ICSNCardiology.org
      - EMAIL_HOST_PASSWORD=CHANGE_ME
      - ALLOW_DEV_BYPASS=False
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - hartbeat-net
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  frontend:
    container_name: hartbeat-frontend
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_BASE_URL=http://2.24.115.93:8005
    ports:
      - "3004:3004"
    restart: unless-stopped
    networks:
      - hartbeat-net

volumes:
  redis_data:
  static_volume:
  media_volume:

networks:
  hartbeat-net:
    driver: bridge
"""

cmd = f"cat > /root/hartbeat-harmony/docker-compose.deploy.yml << 'COMPOSEEOF'\n{compose_content}\nCOMPOSEEOF"
stdin, stdout, stderr = client.exec_command(cmd)
err = stderr.read().decode('utf-8', errors='ignore').strip()
print(f"Compose created: {err if err else 'OK'}")

# Verify
stdin, stdout, stderr = client.exec_command('cat /root/hartbeat-harmony/docker-compose.deploy.yml | head -20')
out = stdout.read().decode('utf-8', errors='ignore').strip()
print(out[:500])

client.close()

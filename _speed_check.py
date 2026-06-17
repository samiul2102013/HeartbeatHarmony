import sys
sys.path.insert(0, r'C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages')
import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Write a shell script on VPS
script = """#!/bin/sh
echo "=== VPS speed tests ==="

echo "1. External URL (via internet loopback):"
curl -s -o /dev/null -w "http=%{http_code} time=%{time_total}s size=%{size_download}bytes speed=%{speed_download}B/s\\n" --max-time 15 "https://api.heartbeatharmony.tech/media/avatars/scaled_63b23995-79ec-4748-9b81-5ac07f0e25c35871072972420631487.jpg"

echo ""
echo "2. Through Nginx internally:"
NGINX=$(docker ps -q -f name=nginx)
docker exec $NGINX sh -c 'curl -s -o /dev/null -w "http=%{http_code} time=%{time_total}s size=%{size_download}bytes\\n" --max-time 10 http://localhost/media/avatars/scaled_63b23995-79ec-4748-9b81-5ac07f0e25c35871072972420631487.jpg'

echo ""
echo "3. Through Daphne directly:"
docker exec $NGINX sh -c 'curl -s -o /dev/null -w "http=%{http_code} time=%{time_total}s size=%{size_download}bytes\\n" --max-time 10 http://backend:8005/media/avatars/scaled_63b23995-79ec-4748-9b81-5ac07f0e25c35871072972420631487.jpg'

echo ""
echo "4. Disk read speed:"
BACKEND=$(docker ps -q -f name=backend)
docker exec $BACKEND sh -c 'dd if=/app/media/avatars/scaled_63b23995-79ec-4748-9b81-5ac07f0e25c35871072972420631487.jpg of=/dev/null bs=1M 2>&1 | tail -1'

echo ""
echo "5. Internet speed test:"
curl -s -o /dev/null -w "speed=%{speed_download}B/s\\n" --max-time 10 "https://api.heartbeatharmony.tech/static/rest_framework/css/bootstrap.min.css"
"""

stdin, stdout, stderr = c.exec_command('cat > /tmp/speed_test.sh', timeout=10)
# Write the script via stdin
transport = c.get_transport()
channel = transport.open_session()
channel.exec_command('cat > /tmp/speed_test.sh')
channel.send(script.encode())
channel.shutdown_write()
channel.makefile('rb', -1).read()

# Make executable and run
stdin, stdout, stderr = c.exec_command('chmod +x /tmp/speed_test.sh && sh /tmp/speed_test.sh', timeout=60)
out = stdout.read().decode()
err = stderr.read().decode()
if out: print(out)
if err: print("ERR:", err)

c.close()

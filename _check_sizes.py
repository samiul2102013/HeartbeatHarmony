import sys
sys.path.insert(0, r'C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages')
import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

stdin, stdout, stderr = c.exec_command('docker ps -q -f name=backend', timeout=15)
container = stdout.read().decode().strip()

stdin, stdout, stderr = c.exec_command(
    'docker exec ' + container + ' sh -c "find /app/media/moods -type f -exec ls -lh {} \\;"',
    timeout=15
)
out = stdout.read().decode()
print("Mood images:")
print(out)

stdin, stdout, stderr = c.exec_command(
    'docker exec ' + container + ' sh -c "find /app/media/avatars -type f -exec ls -lh {} \\;"',
    timeout=15
)
out = stdout.read().decode()
print("Avatars:")
print(out)

c.close()

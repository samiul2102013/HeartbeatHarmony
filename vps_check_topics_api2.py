import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = r'''import urllib.request, json, ssl

# Login
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    "https://api.heartbeatharmony.tech/api/auth/login/",
    data=json.dumps({"email": "support@icsncardiology.org", "password": "Admin@123456"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req, context=ctx)
data = json.loads(resp.read())
access = data["data"]["access"]

# Get topics
req2 = urllib.request.Request(
    "https://api.heartbeatharmony.tech/api/admin/study/topics/",
    headers={"Authorization": f"Bearer {access}"},
)
resp2 = urllib.request.urlopen(req2, context=ctx)
print(json.dumps(json.loads(resp2.read()), indent=2))
'''

sftp = c.open_sftp()
with sftp.open("/tmp/check_topics.py", "w") as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/check_topics.py hartbeat-backend:/tmp/check_topics.py && docker exec hartbeat-backend python /tmp/check_topics.py 2>&1")
print(stdout.read().decode()[:2000])
c.close()

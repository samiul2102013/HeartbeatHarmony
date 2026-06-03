import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = r'''import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://api.heartbeatharmony.tech/api/auth/login/",
    data=json.dumps({"email":"support@icsncardiology.org","password":"Admin@123456"}).encode(),
    headers={"Content-Type":"application/json"})
resp = urllib.request.urlopen(req, context=ctx)
access = json.loads(resp.read())["data"]["access"]

# Test habit templates endpoint (used by frontend dropdown)
req2 = urllib.request.Request("https://api.heartbeatharmony.tech/api/admin/habit-templates/",
    headers={"Authorization": f"Bearer {access}"})
resp2 = urllib.request.urlopen(req2, context=ctx)
print("Habit Templates:", json.dumps(json.loads(resp2.read()), indent=2)[:500])

# Test habits endpoint (for comparison)
req3 = urllib.request.Request("https://api.heartbeatharmony.tech/api/admin/habits/",
    headers={"Authorization": f"Bearer {access}"})
resp3 = urllib.request.urlopen(req3, context=ctx)
print("\nHabits:", json.dumps(json.loads(resp3.read()), indent=2)[:500])
'''

sftp = c.open_sftp()
with sftp.open("/tmp/verify_apis.py", "w") as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/verify_apis.py hartbeat-backend:/tmp/verify_apis.py && docker exec hartbeat-backend python /tmp/verify_apis.py 2>&1")
print(stdout.read().decode()[:1000])

c.close()

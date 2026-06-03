import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

script = r'''import urllib.request, json, ssl

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

boundary = "----FormBoundary7MA4YWxkTrZu0gW"
body = (
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"habit_template\"\r\n\r\n1\r\n"
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"title\"\r\n\r\nTest Material PDF\r\n"
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"material_type\"\r\n\r\npdf\r\n"
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"description\"\r\n\r\n\r\n"
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"video_url\"\r\n\r\n\r\n"
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"is_active\"\r\n\r\ntrue\r\n"
    "--" + boundary + "--\r\n"
).encode()

req2 = urllib.request.Request(
    "https://api.heartbeatharmony.tech/api/admin/habit-materials/",
    data=body,
    headers={
        "Authorization": f"Bearer {access}",
        "Content-Type": "multipart/form-data; boundary=" + boundary,
    },
)
try:
    resp2 = urllib.request.urlopen(req2, context=ctx)
    print("Success:", json.dumps(json.loads(resp2.read()), indent=2))
except urllib.error.HTTPError as e:
    print("Error:", e.code)
    print("Body:", e.read().decode()[:1000])
'''

sftp = c.open_sftp()
with sftp.open("/tmp/test_habit_material2.py", "w") as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/test_habit_material2.py hartbeat-backend:/tmp/test_habit_material2.py && docker exec hartbeat-backend python /tmp/test_habit_material2.py 2>&1")
print(stdout.read().decode()[:2000])
c.close()

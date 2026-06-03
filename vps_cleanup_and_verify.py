import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

# Clean up test material
cmd = 'docker exec hartbeat-postgres psql -U hartbeat -d hartbeat_db -c "DELETE FROM habit_materials WHERE title = \'Test Material PDF\'; DELETE FROM habits WHERE activity_name = \'Maditation\' AND user_id = 1 AND source_template_id = 1;" 2>&1'
stdin, stdout, stderr = c.exec_command(cmd)
print("Cleanup:", stdout.read().decode()[:200])

# Verify API for study materials and topics
script = r'''import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://api.heartbeatharmony.tech/api/auth/login/",
    data=json.dumps({"email":"support@icsncardiology.org","password":"Admin@123456"}).encode(),
    headers={"Content-Type":"application/json"})
resp = urllib.request.urlopen(req, context=ctx)
access = json.loads(resp.read())["data"]["access"]

req2 = urllib.request.Request("https://api.heartbeatharmony.tech/api/admin/study/materials/",
    headers={"Authorization": f"Bearer {access}"})
resp2 = urllib.request.urlopen(req2, context=ctx)
print("Materials:", json.dumps(json.loads(resp2.read()), indent=2)[:500])
'''

sftp = c.open_sftp()
with sftp.open("/tmp/check_study_api.py", "w") as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = c.exec_command("docker cp /tmp/check_study_api.py hartbeat-backend:/tmp/check_study_api.py && docker exec hartbeat-backend python /tmp/check_study_api.py 2>&1")
print(stdout.read().decode()[:1000])

c.close()

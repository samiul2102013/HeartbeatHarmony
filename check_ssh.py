import paramiko
HOST='2.24.115.93'; USER='root'; PASS='HartbeatWellness@Portia123'
c=paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, look_for_keys=False, allow_agent=False, timeout=10)
print('Connection OK from this machine')
i,o,e=c.exec_command("grep -E 'PasswordAuthentication|PubkeyAuthentication' /etc/ssh/sshd_config | grep -v '^#'")
for line in o.read().decode().split('\n'):
    if line.strip(): print(line)
i,o,e=c.exec_command("grep -E 'AllowUsers|Port' /etc/ssh/sshd_config | grep -v '^#'")
for line in o.read().decode().split('\n'):
    if line.strip(): print(line)
c.close()

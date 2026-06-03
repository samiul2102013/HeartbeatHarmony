import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

queries = [
    ("Habits", "SELECT id, user_id, activity_name FROM habits;"),
    ("Habit Templates", "SELECT id, activity_name FROM habit_templates;"),
    ("Study Topics", "SELECT id, title FROM study_topics;"),
    ("Habit Materials", "SELECT id, habit_id, title FROM habit_materials;"),
]

for label, sql in queries:
    cmd = 'docker exec hartbeat-postgres psql -U hartbeat -d hartbeat_db -c "' + sql.replace('"', '\\"') + '" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    print(f"--- {label} ---")
    print(out[:500] if out else "(empty)")
    print()

c.close()

import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('2.24.115.93', username='root', password='HartbeatWellness@Portia123')

queries = [
    ("Habit (table habits)", "SELECT id, user_id, activity_name FROM habits;"),
    ("HabitTemplate (table habits_habittemplate)", "SELECT id, activity_name FROM habits_habittemplate;"),
    ("StudyTopic (table study_topic)", "SELECT id, title FROM study_topic;"),
    ("HabitMaterial (table habits_habitmaterial)", "SELECT id, habit_id, title FROM habits_habitmaterial;"),
]

for label, sql in queries:
    cmd = 'docker exec hartbeat-postgres psql -U hartbeat -d hartbeat_db -c "' + sql.replace('"', '\\"') + '" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"--- {label} ---")
    print(out[:500] if out else "(empty)")
    if err:
        print(f"ERR: {err[:200]}")
    print()

c.close()

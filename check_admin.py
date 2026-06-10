from apps.accounts.models import User
admins = User.objects.filter(role='admin')
for u in admins:
    print(f'id={u.id} email={u.email} username={u.username} is_staff={u.is_staff} is_superuser={u.is_superuser}')
u = User.objects.filter(email='support@ICSNCardiology.org').first()
if u:
    print(f'Found: id={u.id} username={u.username} is_staff={u.is_staff} is_superuser={u.is_superuser}')
    print(f'Password OK: {u.check_password("Admin@123456")}')
else:
    print('User not found')

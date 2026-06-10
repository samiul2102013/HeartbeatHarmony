from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    class Plan(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Pro'

    email = models.EmailField(unique=True)
    institute_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    plan = models.CharField(max_length=10, choices=Plan.choices, default=Plan.FREE)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #email verification fields
    email_verified = models.BooleanField(default=False)
    email_verify_token = models.CharField(max_length=64, blank=True, null=True)
    email_verification_code = models.CharField(max_length=10, blank=True, null=True)
    email_verification_code_created = models.DateTimeField(null=True, blank=True)
    
    #password reset fields
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    password_reset_otp = models.CharField(max_length=10, blank=True, null=True)
    password_reset_otp_created = models.DateTimeField(null=True, blank=True)
    password_reset_new_password = models.CharField(max_length=255, blank=True, null=True)
    check_ins = models.IntegerField(default=0)
    quiz_test = models.IntegerField(default=0)
    Rating = models.IntegerField(default=0)

    class Meta:
        db_table = 'users'

    @property
    def is_pro(self):
        return self.plan == self.Plan.PRO

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN
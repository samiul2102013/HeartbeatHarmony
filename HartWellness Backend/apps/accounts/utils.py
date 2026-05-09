from django.utils import timezone
import secrets

from django.core.mail import send_mail
from django.conf import settings


def generate_verification_token():
    return secrets.token_hex(16)


def generate_verification_code(length=6):
    upper_bound = 10 ** length
    return f"{secrets.randbelow(upper_bound):0{length}d}"

def send_verification_email(user, request):
    """Send email verification OTP to newly registered user."""
    token = str(user.email_verify_token or '')
    code = str(user.email_verification_code or '')
    verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"
    
    send_mail(
        subject="Verify your HeartBeat Harmony email",
        message = (
            f"Hi {user.username}, \n\n"
            f"Your verification code is: {code}\n\n"
            f"If you are using the web app, you can also verify with this link:\n\n"
            f"{verify_url}\n\n"
            f"Thank you!"
        ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user.email],
        fail_silently=False,
                
    )

def send_login_verification_otp(user):
    """Send OTP to unverified user attempting to login."""
    otp = generate_verification_code()
    user.email_verification_code = otp
    user.email_verification_code_created = timezone.now()
    user.save(update_fields=['email_verification_code', 'email_verification_code_created'])
    
    send_mail(
        subject="HeartBeat Harmony Login Verification",
        message = (
            f"Hi {user.username}, \n\n"
            f"You attempted to log in. Please verify your email using this OTP: {otp}\n\n"
            f"This OTP will expire in 1 hour.\n\n"
            f"If you didn't request this, please ignore this email."
        ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user.email],
        fail_silently=False,
    )
    
def send_password_reset_email(user):
    token = str(user.password_reset_token)
    otp = str(user.password_reset_otp or '')
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={token}"
    send_mail(
        subject="Reset your HeartBeat Harmony password",
        message = (
            f"Hi {user.username}, \n\n"
            f"You requested a password reset. Use this OTP to reset your password:\n\n"
            f"{otp}\n\n"
            f"Or use this token to reset your password:\n\n"
            f"{token}\n\n"
            f"Or open this link:\n\n"
            f"{reset_url}\n\n"
            f"This token will expire in 1 hour.\n\n"
            f"If you didn't request this, please ignore this email."
        ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user.email],
        fail_silently=False,
    )
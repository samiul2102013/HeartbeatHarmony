import logging
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_verification_token():
    return secrets.token_hex(16)


def generate_verification_code(length=6):
    # Use secrets for cryptographically strong OTP (not random which is predictable)
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def send_verification_email(user, request):
    """Send email verification OTP to newly registered user.

    Returns True on success, False on SMTP failure. Logs error for monitoring.
    """
    token = str(user.email_verify_token or '')
    code = str(user.email_verification_code or '')
    verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"

    try:
        send_mail(
            subject="Verify your HeartBeat Harmony email",
            message=(
                f"Hi {user.username}, \n\n"
                f"Your verification code is: {code}\n\n"
                f"If you are using the web app, you can also verify with this link:\n\n"
                f"{verify_url}\n\n"
                f"Thank you!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Verification email sent to %s", user.email)
        return True
    except Exception:
        logger.exception("Failed to send verification email to %s", user.email)
        return False

def send_login_verification_otp(user):
    """Send OTP to unverified user attempting to login.
    Reuses the existing OTP if it was generated within the last 5 minutes
    to avoid flooding the user with emails."""
    OTP_RESEND_WINDOW_MINUTES = 5

    existing_code = user.email_verification_code
    existing_created = user.email_verification_code_created

    if (
        existing_code
        and existing_created
        and (timezone.now() - existing_created).total_seconds() < OTP_RESEND_WINDOW_MINUTES * 60
    ):
        otp = existing_code
    else:
        otp = generate_verification_code()
        user.email_verification_code = otp
        user.email_verification_code_created = timezone.now()
        user.save(update_fields=['email_verification_code', 'email_verification_code_created'])

    try:
        send_mail(
            subject="HeartBeat Harmony Login Verification",
            message=(
                f"Hi {user.username}, \n\n"
                f"You attempted to log in. Please verify your email using this OTP: {otp}\n\n"
                f"This OTP will expire in 1 hour.\n\n"
                f"If you didn't request this, please ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Login OTP sent to %s", user.email)
        return True
    except Exception:
        logger.exception("Failed to send login OTP to %s", user.email)
        return False


def send_password_reset_email(user):
    """Send password reset OTP/token. Returns True on success."""
    token = str(user.password_reset_token)
    otp = str(user.password_reset_otp or '')
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={token}"
    try:
        send_mail(
            subject="Reset your HeartBeat Harmony password",
            message=(
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
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Password reset OTP sent to %s", user.email)
        return True
    except Exception:
        logger.exception("Failed to send password reset email to %s", user.email)
        return False
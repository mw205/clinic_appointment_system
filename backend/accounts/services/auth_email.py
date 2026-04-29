import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .email_service import send_email

logger = logging.getLogger(__name__)

def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = f"{settings.FRONTEND_RESET_PASSWORD_URL}?uid={uid}&token={token}"

    subject = "Reset your password"
    message = f"""
Hi {user.first_name},

Click the link below to reset your password:

{reset_link}

If you did not request this, ignore this email.
"""
    try:
        send_email(subject=subject, message= message, recipient_list= [user.email])
        logger.info("Password reset email sent to %s", user.email)
    except Exception as e:
        logger.exception("Failed to send password reset email to %s", user.email)


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_link = f"{settings.FRONTEND_VERIFY_EMAIL_URL}?uid={uid}&token={token}"

    subject = "Verify your email"
    message = f"""Hi {user.first_name},
Please click the link below to verify your email address:
{verify_link}
If you did not create an account, please ignore this email.
"""
    
    try:
        send_email(
                subject=subject,
                message=message,
                recipient_list=[user.email]
            )
        logger.info("Verification email sent to %s", user.email)
    except Exception as e:
        logger.exception("Failed to send verification email to %s", user.email)

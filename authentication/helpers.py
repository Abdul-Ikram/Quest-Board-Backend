from datetime import timedelta
from .models import EmailVerification, PasswordReset
import secrets
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

def generate_otp():
    return f"{secrets.randbelow(10**6):06}"

def send_email(user, email_type, otp=None):
    """
    Sends an email to the user for a specific purpose.
    
    Parameters:
    - user: The user object.
    - email_type: Purpose of the email. Accepts 'registration', 'password_reset', 'otp_regeneration'.
    - otp: Optional. OTP to include in the email. If not provided, generates a new one.
    """
    if not otp:
        otp = generate_otp()

    expiration_time = now() + timedelta(minutes=10)

    if email_type == 'registration':
        subject = "Verify Your Email Address"
        template_name = 'email_verification.html'
        EmailVerification.objects.create(
            user=user,
            otp=otp,
            expires_at=expiration_time,
        )
    elif email_type == 'password_reset':
        subject = "Password Reset Request"
        template_name = 'password_reset.html'
        PasswordReset.objects.update_or_create(
            user=user,
            defaults={
                'otp': otp,
                'expires_at': expiration_time,
                'is_used': False,
            }
        )
    elif email_type == 'otp_regeneration':
        subject = "Regenerate OTP"
        template_name = 'email_verification.html'
        EmailVerification.objects.create(
            user=user,
            otp=otp,
            expires_at=expiration_time,
        )
    else:
        raise ValueError("Invalid email_type specified.")

    # Render email content
    email_body = render_to_string(template_name, {'otp': otp, 'user': user})

    # Send the email
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=email_body,
    )

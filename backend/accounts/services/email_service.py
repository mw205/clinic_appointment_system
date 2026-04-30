from django.conf import settings
from django.core.mail import get_connection, EmailMessage


def send_email(subject, message, recipient_list):
    connection = get_connection()

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_list,
        connection=connection,
    )

    email.send(fail_silently=False)

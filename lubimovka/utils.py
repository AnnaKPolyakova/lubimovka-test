from django.core import mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from config.settings import EMAIL_HOST_USER


def email_is_valid(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_email(to_email, code):
    subject = 'YaMDB confirmation code'
    to = to_email
    text_content = f'''Your confirmation code from YaMDB.\n
                        Keep it secret: {code}'''
    mail.send_mail(
        subject, text_content,
        EMAIL_HOST_USER, [to],
        fail_silently=False
    )

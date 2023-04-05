from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(email, token):
    subject = 'Confirmação de Token'
    link = f'http://127.0.0.1:8000/blogcapyba/?token={token}'
    message = f'Clique no link para autenticar seu usario: {link}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
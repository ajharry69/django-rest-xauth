import threading

from django.core.mail import EmailMultiAlternatives


def send_mail_async(subject: str, body_p: str, body_f: str, recipients: list, sender: str, reply_to: list, ):
    """
    Asynchronously send mail with a body compose of a plain and an alternative HTML formatted-body
    """
    mc = EmailMultiAlternatives(subject=subject, body=body_p, from_email=sender, to=recipients, reply_to=reply_to)
    mc.attach_alternative(body_f, "text/html")
    threading.Thread(target=mc.send, args=(False,)).start()

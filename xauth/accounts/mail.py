import threading

from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string, TemplateDoesNotExist

from xauth.internal_settings import SENDER_ADDRESS, SENDER_ADDRESS_PASSWORD, REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES, APP_NAME

__all__ = ["Mail"]


class Mail:
    def __init__(self, subject=None, recipients=None):
        self._sender = SENDER_ADDRESS
        self._sender_password = SENDER_ADDRESS_PASSWORD
        self._subject = subject
        self._recipients = recipients
        self._reply_to = REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES

    def add_recipient(self, recipient):
        self._recipients = self._recipients or set()
        self._recipients.add(recipient)
        return self

    def send(self, template_name, context=None, request=None, sync=False):
        if context:
            context.setdefault("subject", self._subject)
            context.setdefault("app_name", APP_NAME)

        mail = EmailMultiAlternatives(
            subject=self._subject,
            to=self._recipients,
            from_email=self._sender,
            reply_to=self._reply_to,
            body=render_to_string(f"accounts/{template_name}.txt", context=context, request=request),
            connection=get_connection(username=self._sender, password=self._sender_password),
        )
        try:
            html = render_to_string(f"accounts/{template_name}.html", context=context, request=request)
            mail.attach_alternative(html, "text/html")
        except TemplateDoesNotExist:
            pass

        if sync:
            return mail.send()
        return threading.Thread(target=mail.send).start()

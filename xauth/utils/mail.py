from xauth.tasks import send_mail_async
from .settings import *


class Mail:
    class Address:
        """
        :param sender: mail `sender` address
        :param recipients: mail `recipient(s)` address(es)
        :param reply_to: email address(es) to send mail base_response to
        """

        def __init__(self, recipients=None, sender: str = ACCOUNTS_EMAIL,
                     reply_to: list = REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES):
            __is_not_iterable = not isinstance(recipients, tuple) or not isinstance(recipients, list)
            self.recipients = [recipients] if __is_not_iterable else recipients
            self.sender = sender
            self.reply_to = reply_to

    @staticmethod
    def send(address: Address, template_name: str, context: dict):
        """
        Asynchronously send mail with a body compose of a plain and an alternative HTML formatted-body
        """

        send_mail_async(address.recipients, address.sender, address.reply_to, template_name, context)

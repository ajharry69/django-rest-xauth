import threading

from templated_email import send_templated_mail

from xauth.internal_settings import *  # noqa


class Mail:
    class Address:
        """
        :param sender: mail `sender` address
        :param recipients: mail `recipient(s)` address(es)
        :param reply_to: email address(es) to send mail base_response to
        """

        def __init__(self, recipients=None, sender="ACCOUNTS_EMAIL", reply_to=REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES):
            self.recipients = [recipients] if not isinstance(recipients, (tuple, list)) else recipients
            self.sender = sender
            self.reply_to = reply_to

    @staticmethod
    def send(address: Address, template_name, context=None):
        """
        Asynchronously send mail with a body compose of a plain and an alternative HTML formatted-body
        """
        threading.Thread(
            target=send_templated_mail,
            kwargs={
                "template_name": template_name,
                "from_email": address.sender,
                "recipient_list": address.recipients,
                "reply_to": address.reply_to,
                "context": context,
                "template_suffix": "EMAIL_TEMPLATE_SUFFIX",
                "template_dir": "EMAIL_TEMPLATES_DIRECTORY"
                if "EMAIL_TEMPLATES_DIRECTORY".endswith("/")
                else f"{'EMAIL_TEMPLATES_DIRECTORY'}/",
            },
        ).start()

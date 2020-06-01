import smtplib
import socket

from xauth.tasks import send_mail_async
from .settings import *


class Mail:
    class Body:
        """
        :param plain: mail body WITHOUT HTML formatting
        :param formatted: mail body WITH HTML formatting
        """

        def __init__(self, plain: str, formatted: str = None):
            self.plain = plain
            if not formatted:
                # formatted not provided, use plain as alternative
                formatted = plain
            self.formatted = formatted

        # def __repr__(self):
        #     return json.dumps(self.__dict__)

    class Address:
        """
        :param sender: mail `sender` address
        :param recipients: mail `recipient(s)` address(es)
        :param reply_to: email address(es) to send mail base_response to
        """
        ACCOUNTS_EMAIL = XAUTH.get('ACCOUNTS_EMAIL', '')
        REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES = XAUTH.get('REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES', '')

        def __init__(self, recipients=None, sender: str = ACCOUNTS_EMAIL,
                     reply_to: list = REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES):
            if recipients is None:
                _recipients = []
            if not isinstance(recipients, tuple) or not isinstance(recipients, list):
                _recipients = [recipients]
            else:
                if isinstance(recipients, list):
                    _recipients = recipients
                else:
                    _recipients = list(recipients)

            self.recipients = _recipients
            self.sender = sender
            self.reply_to = reply_to

    class Templates:
        @staticmethod
        def password_reset(user, password) -> tuple:
            # Non-HTML formatted password reset mail
            e = 'p'  # Element
            name = user.get_short_name()
            app = XAUTH.get('APP_NAME', '')

            plain = f"""Hi {name},
Please use "{password}"(without the quotes) as temporary password to reset your {app} account password.

NOTE: the password will expire shortly!

You received this email because you recently requested for a password reset for your {app} account. If you did not,
kindly discard or ignore this email."""

            # HTML formatted password reset mail
            formatted = f"""Hi {name},
<{e}>Please use <strong>{password}</strong> as temporary password to reset your {app} account password.</{e}>

<{e}><strong>NOTE:</strong> the password will expire shortly!</{e}>

<{e}>You received this email because you recently requested for a password reset for your {app} account. If you did not,
kindly discard or ignore this email.</{e}>"""

            return plain, formatted

        @staticmethod
        def account_verification(user, code, welcome: bool = True) -> tuple:
            # Non-HTML formatted password reset mail
            e = 'p'  # Element
            name = user.get_short_name()
            app = XAUTH.get('APP_NAME', '')
            app_name = f'{app} ' if not welcome else ' '
            welcome_message = f"Hi {name}, welcome to {app}!" if welcome else ""

            plain = f"""{welcome_message}
Please use "{code}"(without the quotes) as verification code to verify your {app_name}account.

NOTE: the verification code will expire shortly!

You received this email because you recently created an account with {app}. If you did not, kindly 
discard or ignore this email.
"""

            # HTML formatted password reset mail
            formatted = f"""{welcome_message},
<{e}>Please use <strong>{code}</strong> as verification code to verify your {app_name}account.</{e}>

<{e}><strong>NOTE:</strong> the verification code will expire shortly!</{e}>

<{e}>You received this email because you recently created an account with {app}. If you did not, kindly 
discard or ignore this email.</{e}>"""

            return plain, formatted

    @staticmethod
    def send(subject: str, body: Body, address: Address):
        """
        Asynchronously send mail with a body compose of a plain and an alternative HTML formatted-body
        :param address:
        :param body:
        :param subject: Title of the email
        """

        try:
            x = 1 + 1
            # TODO: Send mail...
            # send_mail_async.delay(subject, body.plain, body.formatted, address.recipients, address.sender,
            #                       address.reply_to)
        except socket.gaierror:
            pass
        except smtplib.SMTPException:
            pass

import threading

from templated_email import send_templated_mail

from xauth.utils.settings import *


def send_mail_async(recipients: list, sender: str, reply_to: list, template_name: str, context: dict):
    """
    Asynchronously send mail with a body compose of a plain and an alternative HTML formatted-body
    """
    context['app_name'] = APP_NAME
    threading.Thread(target=send_templated_mail, kwargs={
        'template_name': template_name,
        'from_email': sender,
        'recipient_list': recipients,
        'reply_to': reply_to,
        'context': context,
        'template_suffix': EMAIL_TEMPLATE_SUFFIX,
        'template_dir': EMAIL_TEMPLATES_DIRECTORY if EMAIL_TEMPLATES_DIRECTORY.endswith(
            '/') else f'{EMAIL_TEMPLATES_DIRECTORY}/',
    }).start()

import importlib
import re

from xauth.utils.settings import XAUTH


def valid_str(string, length: int = 1) -> bool:
    """
    Checks for `string`'s null(not None and length) status

    :param string: str checked for validity
    :param length: minimum length `string` should have
    :return: True if `string` is of `length`
    """
    return string is not None and isinstance(string, str) and len(string) > length - 1


def reset_empty_nullable_to_null(obj, fields):
    """
    Reset '' in named attributes contained in `fields` to None otherwise the provided 
    value is retained
    
    :param obj: object(class instance) containing attributes in `field`
    :param fields: an iterable(list/tuple) of string names of attributes contained in 
    `self`
    """
    for f in fields:
        val = getattr(obj, f)
        if isinstance(val, str) and not valid_str(val):
            setattr(obj, f, None)


def is_http_response_success(status_code: int) -> bool:
    """
    :returns `True` if `status_code` is a 3-digit number starting with 2 and `False` otherwise
    """
    return re.match(r'^2\d{2}$', str(status_code)) is not None


def get_class(module_class_name: str, default):
    """
    Gets a class "name" from `module_class_name`. Example, 'xauth.views.SignInView' would return `SignInView`
    """
    if valid_str(module_class_name):
        module_name, class_name = module_class_name.rsplit('.', 1)
        return getattr(importlib.import_module(module_name), class_name)
    return default

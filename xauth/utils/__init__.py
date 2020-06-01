import re

from rest_framework import status, response as drf_response


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
    :return: list of attribute names that raised AttributeError in the process
    """
    failed = []
    for f in fields:
        try:
            val = getattr(obj, f)
            if valid_str(val) is False:
                setattr(obj, f, None)
        except AttributeError:
            failed.append(f)
    return failed


def get_204_wrapped_response(r: drf_response.Response):
    if not r.data or r.status_code == status.HTTP_204_NO_CONTENT:
        return drf_response.Response(status=status.HTTP_204_NO_CONTENT)
    return get_wrapped_response(r)


def get_wrapped_response(r: drf_response.Response):
    from .response import APIResponse
    from .settings import XAUTH
    if XAUTH.get('WRAP_DRF_RESPONSE', True):
        metadata, debug_message, message, payload, response_data, response_status_code = (
            None, None, None, None, r.data, r.status_code,)
        if isinstance(response_data, str):
            message = response_data
            if is_http_response_success(response_status_code):
                # the response could probably be expected as payload
                payload = response_data
        elif isinstance(response_data, dict):
            _msg = response_data.get('message', response_data.get('success', response_data.get('error', None)))
            metadata = response_data.pop('metadata', response_data.pop('meta', None))
            if valid_str(_msg):
                message = _msg
            else:
                # payload should not be None
                payload = response_data.pop('payload', response_data)
        else:
            payload = response_data

        if valid_str(message):
            try:
                message, debug_message = tuple(re.sub(r'^#|#$', '', message).split('#', 1))
            except ValueError:
                pass

        _response = APIResponse(payload=payload, message=message, debug_message=debug_message, metadata=metadata,
                                status_code=response_status_code)
        return drf_response.Response(_response.response(), status=_response.status_code)
    else:
        return r


def is_http_response_success(status_code: int) -> bool:
    return re.match(r'^2\d{2}$', str(status_code)) is not None

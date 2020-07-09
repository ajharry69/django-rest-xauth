from rest_framework import views, status
from rest_framework.response import Response

from xauth.utils import valid_str
from xauth.utils.response import ErrorResponse


def wrap_error_response_data(ed, **kwargs):
    msg, d_msg, metadata, delimiter = ed, None, None, '#'
    if delimiter in ed:
        msg, d_msg = tuple(ed.split(delimiter, 1))
        if delimiter in d_msg:
            d_msg, metadata = tuple(d_msg.split(delimiter, 1))
    extra_errors = metadata.split(delimiter) if metadata else None
    return ErrorResponse(
        message=msg, debug_message=d_msg,
        extra_errors=extra_errors,
        **kwargs,
    ).data


def exception_handler(exception, context):
    response = views.exception_handler(exception, context)
    response = Response(data={
        'detail': '#'.join([x for x in exception.args if valid_str(x)]),  # only join strings
        'metadata': exception.args,
    }, status=status.HTTP_400_BAD_REQUEST) if response is None else response
    error_data = response.data
    ed = error_data.get('detail') if isinstance(error_data, dict) else None
    error_data = wrap_error_response_data(ed, errors=exception.args, **error_data)
    # update rest_frameworks error data
    response.data.update(error_data)
    return response

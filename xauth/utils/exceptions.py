from rest_framework import views, status
from rest_framework.response import Response

from xauth.utils.response import ErrorResponse


def wrap_error_response_data(ed, **kwargs):
    msg, d_msg, metadata, delimiter = ed, None, None, '#'
    if delimiter in ed:
        msg, d_msg = tuple(ed.split(delimiter, 1))
        if delimiter in d_msg:
            d_msg, metadata = tuple(d_msg.split(delimiter, 1))
    return ErrorResponse(message=msg, debug_message=d_msg, metadata=metadata, **kwargs).data


def exception_handler(exception, context):
    response = views.exception_handler(exception, context)
    response = Response(data={
        'detail': '#'.join(exception.args),
        'metadata': exception.args,
    }, status=status.HTTP_400_BAD_REQUEST) if response is None else response
    erd = response.data
    ed = erd.get('detail') if isinstance(erd, dict) else None
    return Response(data=wrap_error_response_data(ed, **erd), status=response.status_code, )

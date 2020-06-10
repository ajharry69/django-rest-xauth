import re

from django.utils.datetime_safe import datetime
from rest_framework import views, status
from rest_framework.response import Response

from xauth.utils import valid_str
from xauth.utils.response import APIResponse


def timestamps_extractor(txt: str):
    """
    Extracts timestamps from a text
    :param txt: text to retrieve timestamps from
    :return: list of retrieved timestamps
    """
    return re.findall(r'\d{10}', txt)


def timestamps_to_dates(timestamps: list):
    """
    Converts `listed` timestamps to it's `datetime` equivalent
    :param timestamps: timestamps to be converted to `datetime`
    :return: list of `datetime's` from `timestamps`
    """
    return list(map(lambda dt: str(datetime.fromtimestamp(float(dt))), timestamps))


def text_with_dated_timestamps(txt: str):
    """
    Replaces `timestamps` found in `txt` to produce understandable `text`
    :param txt: text whose timestamps are to be replaced
    :return: string with dated timestamps
    """
    try:
        st = re.split(r'\d{10}', txt)
        tts = timestamps_to_dates(timestamps_extractor(txt))

        # if len(st) > 1:
        #     st.insert(1, tts[0])
        # if len(st) > 3:
        #     st.insert(3, tts[1])
        return ''.join(st)
    except TypeError as te:
        return None


def exception_handler(exception, context):
    __field_detail = 'detail'
    response = views.exception_handler(exception, context)
    response = Response(data={
        __field_detail: '#'.join(exception.args)
    }, status=status.HTTP_400_BAD_REQUEST) if response is None else response
    erd = response.data
    if isinstance(erd, dict) and __field_detail in erd:
        ed = str(erd[__field_detail])
        api_response = wrap_error_response(ed, response)
        # Update response's data dictionary
        erd.update(api_response.response())
        del response.data[__field_detail]
    # if isinstance(erd, list):
    #     api_response = wrap_error_response('#'.join(erd), response)
    #     return drf_response.Response(api_response.response(), status=response.status_code)

    return response


def wrap_error_response(ed, response):
    msg, d_msg, metadata, delimiter = ed, None, None, '#'
    if delimiter in ed:
        msg, d_msg = tuple(ed.split(delimiter, 1))
        if delimiter in d_msg:
            d_msg, metadata = tuple(d_msg.split(delimiter, 1))
    msg = msg if valid_str(msg) else None
    d_msg = d_msg if valid_str(d_msg) else None
    metadata = metadata if valid_str(metadata) else None
    return APIResponse(message=msg, status_code=response.status_code, debug_message=text_with_dated_timestamps(d_msg),
                       metadata=metadata, )

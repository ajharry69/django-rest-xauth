from rest_framework import status


class APIResponse:
    """
    Builds an api base_response that can be sent to the client
    :param message: Message to accompany the `Response`
    :param debug_message: Similar to `message` except it's not shown to the user. It's used for debugging
    :param payload: data
    :param is_error: if `True` response is considered an error. Default value is determined by `status_code` value i.e.
    if `status_code` is within 200..300 range then `is_error` = `False`
    :param status_code: HTTP response status code. **N/B:** Consider using **`from rest_framework import status`**
    """
    __attr_status_code = 'status_code'
    __attr_metadata = 'metadata'
    __attr_payload = 'payload'
    __attr_debug_message = 'debug_message'
    __attr_message = 'message'
    __attr_is_error = 'is_error'
    __success_range = range(200, 300)

    def __init__(self, message: str = None, debug_message=None, payload=None, is_error: bool = True,
                 status_code: int = status.HTTP_200_OK, metadata=None):
        self.__is_error = is_error and status_code not in self.__success_range
        self.__message = message
        self.__debug_message = debug_message
        self.__payload = payload
        self.__status_code = status_code
        self.__metadata = metadata

    @property
    def is_error(self):
        return self.__is_error and self.status_code not in self.__success_range

    @is_error.setter
    def is_error(self, value=True):
        self.__is_error = value

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, value):
        self.__message = value

    @property
    def debug_message(self):
        return self.__debug_message

    @debug_message.setter
    def debug_message(self, value):
        self.__debug_message = value

    @property
    def payload(self):
        return self.__payload

    @payload.setter
    def payload(self, value):
        self.__payload = value

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        self.__metadata = value

    @property
    def status_code(self):
        return self.__status_code

    @status_code.setter
    def status_code(self, value=status.HTTP_200_OK):
        self.__status_code = value

    # @property
    def response(self):
        _response = {
            self.__attr_is_error: self.is_error,
            self.__attr_status_code: self.status_code,
            self.__attr_message: self.message,
            self.__attr_debug_message: self.debug_message,
            self.__attr_payload: self.payload,
            self.__attr_metadata: self.metadata
        }

        if not self.message:
            _response.pop(self.__attr_message)

        if not self.debug_message:
            _response.pop(self.__attr_debug_message)

        if not self.payload:
            _response.pop(self.__attr_payload)

        if not self.metadata:
            _response.pop(self.__attr_metadata)

        return _response

    def __repr__(self):
        return self.response()

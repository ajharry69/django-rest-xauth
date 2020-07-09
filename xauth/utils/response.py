import json


class ErrorResponse:

    def __init__(self, error=None, **kwargs):
        self.error = error
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    @property
    def data(self):
        return dict((k, v) for k, v in self.__dict__.items() if v)

    def __repr__(self):
        return json.dumps(self.data)

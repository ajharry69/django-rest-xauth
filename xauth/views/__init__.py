from rest_framework import status, permissions, views
from rest_framework.response import Response

from xauth.utils import get_unique_identifier


class _BaseAPIView(views.APIView):
    many = False
    # on provides (`dict`) data usable in `serializer_class_response`
    serializer_class = None
    # does normal operations of `serializer_class` would it not have been used to provide data
    serializer_class_response = None
    permission_classes = [permissions.AllowAny, ]

    def process_request(self, request, success_status_code: int = status.HTTP_200_OK, instance=None):
        try:
            request_data = self.get_request_data(request)
            serializer_class = self.serializer_class_response or self.serializer_class
            serializer = serializer_class(
                instance=instance,
                data=request_data,
                many=self.many,
                context={'request': request},
            )
            if serializer.is_valid():
                self.on_valid_response_serializer(serializer)
                data, code = serializer.data, success_status_code
            else:
                raise Exception(serializer.errors)
        except Exception as e:
            data, code = e.args, status.HTTP_400_BAD_REQUEST
        return Response(data=data, status=code)

    def get_request_data(self, request):
        request_data = request.data or request.query_params
        # noinspection PyBroadException
        try:
            if get_unique_identifier(self.serializer_class) == get_unique_identifier(self.serializer_class_response):
                # let response serializer handle default request data if they are of same type
                raise Exception("serializers are of same type")
            serializer_class = self.serializer_class or self.serializer_class_response
            serializer = serializer_class(
                data=request_data,
                context={'request': request},
            ) if serializer_class else None
            if serializer and serializer.is_valid(True):
                request_data = self.on_valid_request_serializer(serializer) or request_data
        except Exception:
            pass
        return request_data

    def on_valid_response_serializer(self, serializer):
        instance = serializer.save()
        self.on_save_success(instance)

    @staticmethod
    def on_valid_request_serializer(serializer):
        # without calling this you won't be able to get data from serializer
        serializer.save()
        return serializer.data

    @staticmethod
    def on_save_success(instance):
        pass


class CreateAPIView(_BaseAPIView):
    def post(self, request, format=None):
        return self.process_request(request, status.HTTP_201_CREATED)

# class RetrieveManyAPIView(_BaseAPIView):
#     many = True
#
#     def get(self, request, format=None):
#         return self.process_request(request)
#
#     def on_valid_response_serializer(self, serializer):
#         pass
#
#
# class CreateRetrieveAPIView(CreateAPIView, RetrieveManyAPIView):
#     pass

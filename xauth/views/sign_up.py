from rest_framework import permissions, views, status
from rest_framework.response import Response

from xauth.serializers.sign_up import SignUpSerializer
from xauth.utils import get_wrapped_response, get_class
from xauth.utils.settings import SIGN_UP_REQUEST_SERIALIZER_CLASSES


class SignUpView(views.APIView):
    # queryset = get_user_model().objects.all()
    serializer_class = get_class(SIGN_UP_REQUEST_SERIALIZER_CLASSES, SignUpSerializer)
    serializer_class_response = SignUpSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None):
        request_data = request.data
        try:
            rqs = self.serializer_class(
                data=request_data,
                context={'request': request},
            )  # request serializer
            request_data = rqs.data if rqs.is_valid() else request_data
        except Exception as ex:
            data, code = ex.args, status.HTTP_400_BAD_REQUEST
            pass
        serializer = self.serializer_class_response(
            data=request_data,
            context={'request': request},
        )
        if serializer.is_valid():
            user = serializer.save()
            self.on_success(user)
            data, code = serializer.data, status.HTTP_201_CREATED
        else:
            data, code = serializer.errors, status.HTTP_400_BAD_REQUEST
        return get_wrapped_response(Response(data=data, status=code))

    @staticmethod
    def on_success(user):
        if user and user.requires_verification:
            token, code = user.request_verification(send_mail=True)

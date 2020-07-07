from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions

from xauth.serializers.sign_up import SignUpSerializer
from xauth.utils import is_http_response_success, get_wrapped_response


class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):
        request_data = request.data
        username = request_data.get('username', request_data.get('email', request_data.get('mobile_number', None)))

        response = super().post(request, *args, **kwargs)
        if is_http_response_success(status_code=response.status_code):
            user = get_user_model().objects.filter(
                Q(username=username) | Q(email=username) | Q(mobile_number=username),
            ).first()
            self.on_success(user)
        return get_wrapped_response(response)

    @staticmethod
    def on_success(user):
        if user and user.requires_verification:
            token, code = user.request_verification(send_mail=True)

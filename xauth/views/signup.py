from xauth.serializers.signup import SignUpSerializer
from xauth.utils import get_class
from xauth.utils.settings import SIGNUP_REQUEST_SERIALIZER, SIGNUP_RESPONSE_SERIALIZER
from xauth.views import CreateAPIView


class SignUpView(CreateAPIView):
    serializer_class = get_class(SIGNUP_REQUEST_SERIALIZER, SignUpSerializer)
    serializer_class_response = get_class(SIGNUP_RESPONSE_SERIALIZER, SignUpSerializer)

    @staticmethod
    def on_save_success(instance):
        if instance and instance.requires_verification:
            token, code = instance.request_verification(send_mail=True)

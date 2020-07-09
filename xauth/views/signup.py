from xauth.serializers.signup import request_serializer_class, response_serializer_class
from xauth.views import CreateAPIView


class SignUpView(CreateAPIView):
    serializer_class = request_serializer_class
    serializer_class_response = response_serializer_class

    @staticmethod
    def on_save_success(instance):
        if instance and instance.requires_verification:
            token, code = instance.request_verification(send_mail=True)

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework import views, status
from rest_framework.response import Response

from xauth.serializers import AuthTokenOnlySerializer


class PasswordResetRequestView(views.APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = AuthTokenOnlySerializer

    @staticmethod
    def post(request, format=None):
        email = request.data.get('email', None)
        try:
            user = request.user
            is_valid_user = user and not isinstance(user, AnonymousUser)
            user = user if is_valid_user else get_user_model().objects.get(email=email)
            token, message = user.request_password_reset(send_mail=True)
            data, status_code = token.tokens, status.HTTP_200_OK
        except get_user_model().DoesNotExist:
            # user not found
            data, status_code = {'error': 'email address is not registered'}, status.HTTP_404_NOT_FOUND
        return Response(data, status=status_code)


class PasswordResetConfirmView(PasswordResetRequestView):
    """
    Attempts to reset(change) authenticated user's password(retrieved from a POST request using
    `temporary_password` as key).

    =============================================================================================

    From the same POST request user can add a `query_param` with **key** = 'operation' and
    **value** being one of ['send', 'resend', 'request'] to be sent a new **temporary password**

    =============================================================================================
    """
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, format=None):
        # should contain a user object if Token authentication(from AuthBackend) was successful
        user, data = request.user, request.data
        operation = request.query_params.get('operation', 'reset').lower()
        if re.match('^(re(send|quest)|send)$', operation):
            # probably a new request for password reset
            # get username to resend the email
            return super(PasswordResetConfirmView, self).post(request, format)
        else:
            # reset password
            t_pass = data.get('temporary_password', data.get('old_password', None))
            n_pass = data.get('new_password', None)
            token, message = user.reset_password(temporary_password=t_pass, new_password=n_pass)
            if token is not None:
                # password reset was successful
                data, status_code = self.serializer_class(user, ).data, None
            else:
                data, status_code = {'error': message}, status.HTTP_400_BAD_REQUEST
        return Response(data, status=status_code or status.HTTP_200_OK)

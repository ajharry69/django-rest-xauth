import re

from rest_framework import views, status
from rest_framework.response import Response

from xauth import permissions
from xauth.serializers import AuthTokenOnlySerializer


class VerificationRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AuthTokenOnlySerializer

    def post(self, request, format=None):
        user = request.user
        # new verification code resend or request is been made
        token, code = user.request_verification(send_mail=True)
        return Response(
            data=self.serializer_class(user, ).data,
            status=status.HTTP_200_OK,
        )


class VerificationConfirmView(VerificationRequestView):
    """
    Attempts to verify authenticated user's verification code(retrieved from a POST request using
    'code' as key).

    =============================================================================================

    From the same POST request user can add a `query_param` with **key** = 'operation' and value
    being one of ['send', 'resend', 'request'] to be sent a new verification code

    =============================================================================================
    """

    def post(self, request, format=None):
        user = request.user
        operation = request.query_params.get('operation', 'confirm').lower()
        if re.match('^(re(send|quest)|send)$', operation):
            # new verification code resend or request is been made
            return super(VerificationConfirmView, self).post(request, format)
        else:
            # verify provided code
            code = request.data.get('code', None)
            token, message = user.verify(code=code)
            if token is not None:
                # verification was successful
                data, status_code = self.serializer_class(user, ).data, None
            else:
                data, status_code = {'error': message}, status.HTTP_400_BAD_REQUEST
        return Response(
            data=data,
            status=status_code or status.HTTP_200_OK,
        )

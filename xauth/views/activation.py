import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework import permissions
from rest_framework import views, status
from rest_framework.response import Response

from xauth.models import Metadata
from xauth.serializers import AuthTokenOnlySerializer


class ActivationRequestView(views.APIView):
    """
    Provides a user with possible account activation methods provided a correct account
    `username` is supplied as part of a POST request.
    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = AuthTokenOnlySerializer

    def post(self, request, format=None):
        request_data = request.data
        username = request_data.get('username') or request_data.get('email')
        user = request.user
        is_valid_user = user and not isinstance(user, AnonymousUser)
        user = user if is_valid_user else get_user_model().objects.filter(
            Q(username=username) | Q(email=username),
        ).first()
        if user:
            # account activation methods. Only include `security_question` if user
            # has a valid question attached to his/her account
            metadata = ['creation_date', ] + (
                ['security_question'] if self.has_valid_security_question(user) else [])
            data = self.serializer_class(user, context={'request': request}, ).data
            data = {'payload': data, 'metadata': metadata, }
            data, status_code = data, status.HTTP_200_OK
        else:
            data = {'error': 'username or email address is not registered', }
            data, status_code = data, status.HTTP_404_NOT_FOUND
        return Response(data, status=status_code)

    @staticmethod
    def has_valid_security_question(user) -> bool:
        """Returns True if security question attached to user's account is usable(valid) or False"""
        metadata = Metadata.objects.filter(user=user, ).first()
        return metadata and metadata.security_question.usable


class ActivationConfirmView(ActivationRequestView):
    """
    Activates a user's account when provided by a correct `answer` in a POST request with a `answer` as key.
    """
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, format=None):
        user, data = request.user, request.data
        operation = request.query_params.get('operation', 'confirm').lower()
        if re.match('^request$', operation):
            # probably a new request for password reset
            # get username to resend the email
            return super().post(request, format)
        else:
            # answer is expected to either be an estimate of account creation date or an answer to security question
            answer = data.get('answer', None)
            token, message = user.activate_account(security_question_answer=answer)
            if token is not None:
                # account activation was successful
                data, status_code = self.serializer_class(user, ).data, None
            else:
                data, status_code = {'error': message}, status.HTTP_400_BAD_REQUEST
        return Response(data, status=status_code or status.HTTP_200_OK)

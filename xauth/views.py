import re

from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework import permissions, generics, views, status, viewsets
from rest_framework.response import Response

from .models import Metadata
from .permissions import *
from .serializers import *
from .utils import get_204_wrapped_response, get_wrapped_response, valid_str, is_http_response_success


class SecurityQuestionView(viewsets.ModelViewSet):
    queryset = SecurityQuestion.objects.filter(usable=True)
    serializer_class = SecurityQuestionSerializer
    permission_classes = [IsSuperUserOrReadOnly, ]


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = USER_LOOKUP_FIELD
    queryset = get_user_model().objects.all()
    serializer_class = profile_serializer_class
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, ]

    def get(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().get(request, *args, **kwargs))

    def put(self, request, *args, **kwargs):
        return get_wrapped_response(super().put(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        return get_wrapped_response(super().patch(request, *args, **kwargs))

    def delete(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().delete(request, *args, **kwargs))


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


class SignInView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AuthSerializer

    def post(self, request, format=None):
        # authentication logic is by default handled by the auth-backend
        user = request.user
        user.update_or_create_access_log(force_create=True)
        serializer = self.serializer_class(user, context={'request': request}, )
        return get_wrapped_response(Response(serializer.data, status=status.HTTP_200_OK))


class SignOutView(views.APIView):
    permission_classes = [permissions.AllowAny, ]

    @staticmethod
    def post(request, format=None):
        user = request.user
        if user and not isinstance(user, AnonymousUser):
            user.update_or_create_access_log()
        logout(request)
        return get_wrapped_response(Response({'success': 'signed out'}, status=status.HTTP_200_OK))


class VerificationRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AuthTokenOnlySerializer

    def post(self, request, format=None):
        user = request.user
        # new verification code resend or request is been made
        token, code = user.request_verification(send_mail=True)
        response = Response(self.serializer_class(user, ).data, status=status.HTTP_200_OK)
        return get_wrapped_response(response)


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
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)


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
        return get_wrapped_response(Response(data, status=status_code))


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
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)


class AddSecurityQuestionView(views.APIView):
    """
    Attaches users selected security question and the corresponding answer
    """
    permission_classes = [permissions.IsAuthenticated, ]

    @staticmethod
    def post(request, format=None):
        user, data = request.user, request.data
        # question can be identified by the question text itself or it's id both of which are
        # expected to be unique
        answer = data.get('answer', data.get('question_answer', None))
        question_id = data.get('question', data.get('id', data.get('question_id', None)))
        question = SecurityQuestion.objects.filter(Q(question=question_id) | Q(id=question_id)).first()
        if question and valid_str(answer):
            # question was found and answer is a valid string
            user.add_security_question(question, answer)
            data, status_code = {'success': 'security question added successfully'}, status.HTTP_200_OK
        else:
            data = {'error': f"invalid {'answer' if question else 'question'}"}
            data, status_code = data, status.HTTP_400_BAD_REQUEST
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)


class ActivationRequestView(views.APIView):
    """
    Provides a user with possible account activation methods provided a correct account
    `username` is supplied as part of a POST request.
    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = AuthTokenOnlySerializer

    def post(self, request, format=None):
        request_data = request.data
        username = request_data.get('username', request_data.get('email', None))
        user = request.user
        is_valid_user = user and not isinstance(user, AnonymousUser)
        user = user if is_valid_user else get_user_model().objects.filter(
            Q(username=username) | Q(email=username),
        ).first()
        if user:
            # account activation methods. Only include `security_question` if user has a valid question attached to
            # his/her account
            metadata = ['creation_date', ] + (['security_question'] if self.has_valid_security_question(user) else [])
            data = self.serializer_class(user, context={'request': request}, ).data
            data = {'payload': data, 'metadata': metadata, }
            data, status_code = data, status.HTTP_200_OK
        else:
            data = {'error': 'username or email address is not registered', }
            data, status_code = data, status.HTTP_404_NOT_FOUND
        return get_wrapped_response(Response(data, status=status_code))

    @staticmethod
    def has_valid_security_question(user) -> bool:
        """Returns True if security question attached to user's account is usable(valid) or False"""
        metadata = Metadata.objects.filter(user=user, ).first()
        return True if (metadata and metadata.security_question.usable) else False


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
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)

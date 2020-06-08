import base64
import re

from django.contrib.auth import get_user_model
from jwcrypto import jwt, jwe
from rest_framework import authentication as drf_auth, exceptions as drf_exception

from xauth.utils import valid_str, settings
from xauth.utils.token import Token


class BasicTokenAuthentication(drf_auth.BaseAuthentication):
    """
    Attempts 3 different authentication methods(Bearer token, Basic, POST request) in order of listing
     before surrendering control to its succeeding Authentication backends
    """
    auth_scheme = 'Bearer'

    def authenticate(self, request):
        address_header_payload = request.META.get('HTTP_X_Forwarded_For', request.META.get('REMOTE_ADDR', None))
        request_url = str(request.build_absolute_uri()).lower()
        auth = None
        authorization_header = drf_auth.get_authorization_header(request)
        auth_header = authorization_header.decode() if isinstance(authorization_header, bytes) else authorization_header
        if valid_str(auth_header):
            # an authorization header was provided
            # separate auth-scheme/auth-type(e.g. Bearer, Token, Basic) from auth-data/auth-payload(e.g. base64url
            # encoding of username & password combination for Basic auth or Bearer|Token value/data)
            auth_scheme_and_payload = auth_header.split()
            if len(auth_scheme_and_payload) > 1:
                auth_response = self.get_user_from_basic_or_token_auth_scheme(auth_scheme_and_payload, request_url)
                if isinstance(auth_response, tuple):
                    user, auth = auth_response
                else:
                    return auth_response  # unknown/unsupported authentication scheme
            else:
                return None  # unknown/unsupported authentication scheme
        else:
            # attempt to authenticate from POST-request data
            username, password = self.get_post_request_username_and_password(request=request)
            user = self.get_user_with_username_and_password(username=username, password=password)
        return self.__get_wrapped_authentication_response(address_header_payload, user, auth, request_url)

    def authenticate_header(self, request):
        return 'Provide a Bearer-token, Basic or POST-request with username and password'

    def get_user_from_jwt_token(self, token, request_url):
        """
        Gets and returns `user` object who the `token` payload data refer

        :param request_url: ...
        :raises AuthenticationFailed if token's payload data does not match to any user in the database
        :param token: JWT token
        :return: user object
        """
        self.auth_scheme = 'Bearer'
        try:
            tk = Token(None)
            claims = tk.get_claims(token=token)
            user_payload = claims.get(tk.payload_key, {})
            user_id = user_payload.get('id', None) if isinstance(user_payload, dict) else user_payload
            subject = claims.get('sub', 'access')
            if settings.VERIFICATION_ENDPOINT in request_url and subject != 'verification':
                raise jwe.JWException(f'tokens is restricted to {subject}')
            elif settings.ACTIVATION_ENDPOINT in request_url and subject != 'activation':
                raise jwe.JWException(f'tokens is restricted to {subject}')
            elif settings.PASSWORD_RESET_ENDPOINT in request_url and subject != 'password-reset':
                raise jwe.JWException(f'tokens is restricted to {subject}')
            else:
                try:
                    return get_user_model().objects.get(pk=user_id) if user_id else None
                except get_user_model().DoesNotExist as ex:
                    raise drf_exception.AuthenticationFailed(f'user not found#{ex.args[0]}')
        except jwt.JWTExpired as ex:
            raise drf_exception.AuthenticationFailed(f'expired token#{ex.args[0]}')
        except jwt.JWTNotYetValid as ex:
            raise drf_exception.AuthenticationFailed(f'token not ready for use#{ex.args[0]}')
        except jwe.JWException as ex:
            raise drf_exception.AuthenticationFailed(f'invalid token#{ex.args[0]}')

    def get_user_from_basic_or_token_auth_scheme(self, auth_scheme_and_credentials, request_url):
        """
        Gets and returns a `user` object from a [Bearer|Token] or Basic authentication schemes

        :raises AuthenticationFailed if either of the schemes does not successfully return a user
        object either because a user was not found matching the obtained credentials or (only
        applicable to Basic authentication scheme|POST request authentication) user was  found but
         the provided password did not match the username
        :param auth_scheme_and_credentials: a pair(in order) of authentication-scheme and credentials
         in a list
        :param request_url: ...
        :return: a tuple of (user,auth) or None if none of the supported/expected authentication
        schemes was found
        """
        # a scheme and payload is probably present. Extract
        auth_scheme = auth_scheme_and_credentials[0].lower()  # expected to be the first
        auth_credentials = auth_scheme_and_credentials[1]  # expected to be the second
        if re.match(r'^(bearer|token)$', auth_scheme):
            # begin jwt-token based authentication
            return self.get_user_from_jwt_token(auth_credentials, request_url), auth_credentials
        elif re.match('^basic$', auth_scheme):
            # begin basic authentication
            username, password = self.get_basic_auth_username_and_password(auth_credentials)
            return self.get_user_with_username_and_password(username=username, password=password), None
        else:
            return None  # unknown/unsupported authentication scheme

    def get_user_with_username_and_password(self, username, password):
        """
        Gets and returns `user` object with matching `username` and `password` combination

        :raises rest_framework.exceptions.AuthenticationFailed if `password` is invalid or when a user
        with `username` does not exist in the database

        :param username: user's username
        :param password: user's "raw" password
        :return: user object or None if both `username` & `password` were None or empty
        """
        self.auth_scheme = 'Basic'
        try:
            if valid_str(username) and valid_str(password):
                user = get_user_model().objects.get_by_natural_key(username)
                if user.check_password(raw_password=password) is False:
                    # user was found but password does not match
                    # log user's failed sign-in attempt
                    password_change_message = user.get_last_password_change_message(locale='en')
                    remaining_attempts = user.update_signin_attempts(failed=True)
                    message = f'invalid username and/or password##{remaining_attempts}#{password_change_message}'
                    raise drf_exception.AuthenticationFailed(message)
            else:
                return None
        except get_user_model().DoesNotExist as ex:
            raise drf_exception.AuthenticationFailed(f'user not found#{ex.args[0]}')
        # sign-in was a success. Reset sign-in attempts to zero
        user.update_signin_attempts(failed=False, )
        return user

    @staticmethod
    def get_basic_auth_username_and_password(credentials):
        """
        Gets and returns username and password combination from a Basic authentication scheme
        https://en.wikipedia.org/wiki/Basic_access_authentication

        :param credentials: the Base64 encoding of ID and password joined by a single colon
        :return: tuple
        """
        return tuple(base64.b64decode(credentials, validate=True).decode().split(':'))

    @staticmethod
    def get_post_request_username_and_password(request):
        """
        Gets and returns username and password combination from Http POST request

        :param request `django.http.HttpRequest`
        :return: tuple of username and password i.e. (username, password)
        """
        post, request_data = request.POST, request.data
        _un_key, _pw_key = settings.POST_REQUEST_USERNAME_FIELD, settings.POST_REQUEST_PASSWORD_FIELD

        if isinstance(request_data, dict):
            # check key count 2
            if len(request_data.keys()) == 2:
                # probably a POST request sign-in request
                username = post.get(_un_key, request_data.get(_un_key, None))
                password = post.get(_pw_key, request_data.get(_pw_key, None))
                return username, password
        return None, None

    @staticmethod
    def get_client_ip(addresses_str):
        """
        [X-Forwarded-For header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)

        :param addresses_str: string of IP addresses separated with commas(,) and or
        spaces much like the standard value of a HTTP X-Forwarded-For header
        :return: the first IP address from a cleansed comma split of `addresses_str`
        or None if `addresses_str` is None
        """
        if addresses_str:
            # addresses where provided, trim off spaces or double
            ip_addresses = re.sub(r'^,+|\s+,*|,+$', '', addresses_str).split(',')
            return ip_addresses[0] if len(ip_addresses) > 0 else ip_addresses
        return None

    def __get_wrapped_authentication_response(self, addresses_str, user, auth, request_url):
        if not user:
            return None
        if user.is_active or settings.ACTIVATION_ENDPOINT in request_url:
            user.device_ip = self.get_client_ip(addresses_str)
            return user, auth
        raise drf_exception.AuthenticationFailed('account was deactivated')

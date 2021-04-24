import re

from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from ipware import get_client_ip
from jwcrypto import jwt, jwe
from rest_framework import authentication, exceptions

from xauth.utils import is_valid_str, settings
from xauth.utils.token import Token

__all__ = ["JWTTokenAuthentication"]


class BaseAuthentication(authentication.BaseAuthentication):
    request = None
    auth_scheme = None

    @cached_property
    def request_url_in_lowercase(self):
        return str(self.request.build_absolute_uri()).lower()

    def authenticate(self, request):
        self.request = request

    def _get_wrapped_response(self, request, user):
        if user.is_active or settings.ACTIVATION_ENDPOINT in self.request_url_in_lowercase:
            user.device_ip = get_client_ip(request)
            return user
        raise exceptions.AuthenticationFailed("account was deactivated")


class JWTTokenAuthentication(BaseAuthentication):
    auth_scheme = "Bearer"

    def authenticate(self, request):
        super().authenticate(request)

        header = authentication.get_authorization_header(self.request)
        auth_header_data = header.decode() if isinstance(header, bytes) else header
        if not is_valid_str(auth_header_data):
            return

        # an authorization header was provided
        # separate auth-scheme/auth-type(e.g. Bearer, Token, Basic) from auth-data/auth-payload(e.g. base64url
        # encoding of username & password combination for Basic auth or Bearer|Token value/data)
        authorization_data = auth_header_data.split()
        if len(authorization_data) > 1:
            auth_scheme = authorization_data[0].lower()  # expected to be the first
            if re.match(r"^(bearer|token)$", auth_scheme):
                user = self.get_user_from_jwt_token(authorization_data[1])
                return self._get_wrapped_response(request, user), authorization_data[1] if user else None
        return None  # unknown/unsupported authentication scheme

    def authenticate_header(self, request):
        return "Provide a Bearer <token>"

    def get_user_from_jwt_token(self, jwt_token):
        try:
            token = Token(None)
            claims = token.get_claims(token=jwt_token)
            user_payload = claims.get(token.payload_key, {})
            user_id = user_payload.get("id", None) if isinstance(user_payload, dict) else user_payload
            subject = claims.get("sub", "access")
            if settings.VERIFICATION_ENDPOINT in self.request_url_in_lowercase and subject != "verification":
                raise jwe.JWException(f"tokens is restricted to {subject}")
            elif settings.ACTIVATION_ENDPOINT in self.request_url_in_lowercase and subject != "activation":
                raise jwe.JWException(f"tokens is restricted to {subject}")
            elif settings.PASSWORD_RESET_ENDPOINT in self.request_url_in_lowercase and subject != "password-reset":
                raise jwe.JWException(f"tokens is restricted to {subject}")
            else:
                try:
                    return get_user_model().objects.get(pk=user_id) if user_id else None
                except get_user_model().DoesNotExist as ex:
                    raise exceptions.AuthenticationFailed(f"user not found#{ex.args[0]}")
        except jwt.JWTExpired as ex:
            raise exceptions.AuthenticationFailed(f"expired token#{ex.args[0]}")
        except jwt.JWTNotYetValid as ex:
            raise exceptions.AuthenticationFailed(f"token not ready for use#{ex.args[0]}")
        except jwe.JWException as ex:
            raise exceptions.AuthenticationFailed(f"invalid token#{ex.args[0]}")

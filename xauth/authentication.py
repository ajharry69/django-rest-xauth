import re

from django.contrib.auth import get_user_model
from django.urls.exceptions import Resolver404, NoReverseMatch
from django.utils.translation import gettext as _
from ipware import get_client_ip
from jwcrypto import jwt, jwe
from rest_framework import authentication, exceptions
from xently.core.loading import get_class

from xauth.internal_settings import AUTH_APP_LABEL

__all__ = ["JWTTokenAuthentication"]


class BaseAuthentication(authentication.BaseAuthentication):
    request = None
    auth_scheme = None

    @property
    def request_url_in_lowercase(self):
        return str(self.request.build_absolute_uri()).lower()

    def authenticate(self, request):
        self.request = request

    @property
    def _is_verification_endpoint(self):
        from xauth.accounts.views import AccountViewSet

        view = AccountViewSet(request=self.request)
        try:
            endpoint = view.reverse_action(view.verify_account.url_name, kwargs=view.request.resolver_match.kwargs)
        except (Resolver404, NoReverseMatch):
            return False
        return endpoint == self.request_url_in_lowercase

    @property
    def _is_activation_endpoint(self):
        from xauth.accounts.views import AccountViewSet

        view = AccountViewSet(request=self.request)
        try:
            endpoint = view.reverse_action(view.activate_account.url_name, kwargs=view.request.resolver_match.kwargs)
        except (Resolver404, NoReverseMatch, AttributeError):
            return False
        return endpoint == self.request_url_in_lowercase

    @property
    def _is_password_reset_endpoint(self):
        from xauth.accounts.views import AccountViewSet

        view = AccountViewSet(request=self.request)
        try:
            endpoint = view.reverse_action(view.reset_password.url_name, kwargs=view.request.resolver_match.kwargs)
        except (Resolver404, NoReverseMatch):
            return False
        return endpoint == self.request_url_in_lowercase

    def _get_wrapped_response(self, request, user):
        if user.is_active or self._is_activation_endpoint:
            user.device_ip = get_client_ip(request)
            return user
        raise exceptions.AuthenticationFailed(_("Account was deactivated"), code="account_deactivated")


class JWTTokenAuthentication(BaseAuthentication):
    auth_scheme = "Bearer"

    def authenticate(self, request):
        super().authenticate(request)

        header = authentication.get_authorization_header(self.request)
        auth_header_data = header.decode() if isinstance(header, bytes) else header
        if not auth_header_data:
            return

        # an authorization header was provided
        # separate auth-scheme/auth-type(e.g. Bearer, Token, Basic) from auth-data/auth-payload(e.g. base64url
        # encoding of username & password combination for Basic auth or Bearer|Token value/data)
        authorization_data = auth_header_data.split()
        if len(authorization_data) > 1:
            if re.match(r"^bearer$", authorization_data[0], flags=re.I):
                user = self.get_user_from_jwt_token(authorization_data[1])
                return self._get_wrapped_response(request, user), authorization_data[1] if user else None
        return None  # unknown/unsupported authentication scheme

    def authenticate_header(self, request):
        return "Provide a Bearer <token>"

    def get_user_from_jwt_token(self, jwt_token):
        try:
            token = get_class(f"{AUTH_APP_LABEL}.token.generator", "Token")(None)
            claims = token.get_claims(token=jwt_token)
            if claims["sub"] != "verification" and self._is_verification_endpoint:
                raise jwe.JWException
            elif claims["sub"] != "activation" and self._is_activation_endpoint:
                raise jwe.JWException
            elif claims["sub"] != "password-reset" and self._is_password_reset_endpoint:
                raise jwe.JWException
            else:
                try:
                    user = get_user_model().from_signed_id(signed_id=claims[token.payload_key]["id"])
                except get_user_model().DoesNotExist:
                    raise exceptions.AuthenticationFailed
                else:
                    if user:
                        return user
                    raise jwt.JWTInvalidClaimValue
        except jwt.JWTExpired:
            raise exceptions.AuthenticationFailed(_("Expired token"), code="expired_token")
        except jwe.JWException:
            raise exceptions.AuthenticationFailed(_("Invalid token"), code="invalid_token")

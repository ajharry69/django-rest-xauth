import re

from django.contrib.auth import get_user_model
from django.urls.exceptions import Resolver404, NoReverseMatch
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from jwcrypto import jwt, jwe
from rest_framework import authentication, exceptions
from xently.core.loading import get_class

from xauth.internal_settings import AUTH_APP_LABEL

__all__ = ["JWTAuthentication", "PasswordResetRequestAuthentication"]


class PasswordResetRequestAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        filter_kwargs = request.data.copy()
        for field_name in request.data:
            if field_name not in get_user_model().get_password_reset_lookup_fields():
                del filter_kwargs[field_name]

        user = get_user_model()._default_manager.filter(**filter_kwargs).first()
        return user, request.data if user else None


class JWTAuthentication(authentication.BaseAuthentication):
    request = None
    auth_scheme = "Bearer"

    @cached_property
    def _auth_view(self):
        return get_class(f"{AUTH_APP_LABEL}.views", "AccountViewSet")(request=self.request)

    def _is_request_from_any_of(self, url_names):
        try:
            endpoints = [
                self._auth_view.reverse_action(url_name, kwargs=self._auth_view.request.resolver_match.kwargs)
                for url_name in url_names
            ]
        except (Resolver404, NoReverseMatch):
            return False
        return self.request.build_absolute_uri() in endpoints

    @property
    def _is_activation_endpoint(self):
        return self._is_request_from_any_of([self._auth_view.activate_account.url_name])

    def authenticate(self, request):
        self.request = request

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
                if user is None:
                    raise exceptions.AuthenticationFailed(_("Invalid bearer token"), code="invalid_token")

                if user.is_active or self._is_activation_endpoint:
                    return user, authorization_data[1]
                raise exceptions.AuthenticationFailed(_("Account was deactivated"), code="account_deactivated")
        return  # unknown/unsupported authentication scheme

    def authenticate_header(self, request):
        return "Provide a Bearer <token>"

    def get_user_from_jwt_token(self, jwt_token):
        try:
            token = get_class(f"{AUTH_APP_LABEL}.token.generator", "Token")(None)
            claims = token.get_claims(token=jwt_token)
            if claims["sub"] == "verification" and (
                not self._is_request_from_any_of(
                    [
                        self._auth_view.verify_account.url_name,
                        self._auth_view.request_verification_code.url_name,
                    ]
                )
            ):
                raise jwe.JWException
            elif claims["sub"] == "password-reset" and (
                not self._is_request_from_any_of(
                    [
                        self._auth_view.reset_password.url_name,
                        self._auth_view.request_temporary_password.url_name,
                    ]
                )
            ):
                raise jwe.JWException
            elif claims["sub"] == "activation" and (not self._is_activation_endpoint):
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

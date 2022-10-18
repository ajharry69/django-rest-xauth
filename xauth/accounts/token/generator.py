import json
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from jwcrypto import jwt
from xently.core.loading import get_class

from xauth.internal_settings import TOKEN_EXPIRY, AUTH_APP_LABEL

__all__ = ["Token"]


class Token(get_class(f"{AUTH_APP_LABEL}.token.key", "TokenKey")):
    DEFAULT_TOKEN_EXPIRY_TIME_DELTAS = {
        "access": timedelta(days=1),
        "activation": timedelta(minutes=30),
        "verification": timedelta(minutes=30),
        "password-reset": timedelta(minutes=30),
    }

    def __init__(self, payload, activation_date=None, expiry_period=None, payload_key=None, subject=None):
        super().__init__()
        self._unencrypted = None
        self._encrypted = None
        self.subject = subject or "access"
        self.payload = payload
        self.payload_key = payload_key or "payload"
        self.activation_date = activation_date
        self.expiry_period = expiry_period or {
            **self.__class__.DEFAULT_TOKEN_EXPIRY_TIME_DELTAS,
            **TOKEN_EXPIRY,
        }[self.subject]

    def __repr__(self):
        return self.encrypted

    @property
    def unencrypted(self):
        if self._unencrypted is None:
            self.refresh()
        return self._unencrypted

    @property
    def encrypted(self):
        if self._encrypted is None:
            self.refresh()
        return self._encrypted

    @property
    def checked_claims(self):
        issue_date = timezone.now().astimezone()
        self.activation_date = issue_date if not self.activation_date else self.activation_date

        expiry_date = self.activation_date + self.expiry_period
        activation_secs = int(self.activation_date.strftime("%s"))
        expiry_secs = int(expiry_date.strftime("%s"))
        assert expiry_secs > activation_secs, "Expiration date must be a date later than activation date"
        return {
            "nbf": activation_secs,
            "exp": expiry_secs,
            "iat": int(issue_date.strftime("%s")),
            "sub": self.subject,
        }

    @property
    def claims(self):
        # convert provided payload to string if it is not already a string or a dictionary
        # self.payload = str(self.payload) if not isinstance(self.payload, dict) else self.payload
        cc = self.checked_claims
        cc[self.payload_key] = self.payload
        return cc

    @property
    def tokens(self):
        if not self.unencrypted or not self.encrypted:
            self.refresh()
        return {"encrypted": self.encrypted, "unencrypted": self.unencrypted}

    def get_claims(self, token=None, is_encrypted=None):
        if is_encrypted is None:
            # This setting would have been better read from `internal_settings` module for
            # documentation and ease of refactor
            is_encrypted = getattr(settings, "XAUTH_VERIFY_ENCRYPTED_TOKEN", True)

        if token is None:
            token = self.encrypted if is_encrypted else self.unencrypted

        assert token is not None, "Call .refresh() first or provide a token"
        token = token.decode() if isinstance(token, bytes) else token

        try:
            token = jwt.JWT(key=self.encryption_key, jwt=token).claims if is_encrypted else token
        except ValueError:
            raise jwt.JWException
        return json.loads(jwt.JWT(key=self.get_jwt_signing_keys()[1], jwt=token).claims)

    def get_payload(self, token=None, is_encrypted=None):
        try:
            return self.get_claims(token, is_encrypted).get(self.payload_key, None)
        except AssertionError:
            return self.payload

    def refresh(self):
        header = {"alg": self.signing_algorithm, "typ": "JWT"}
        # unencrypted token
        token = jwt.JWT(header, self.claims, check_claims=self.checked_claims, algs=self.ALLOWED_SIGNING_ALGORITHMS)
        token.make_signed_token(key=self.get_jwt_signing_keys()[0])
        self._unencrypted = token.serialize()
        header = {"alg": "ECDH-ES", "enc": "A256GCM"}
        # encrypted token
        e_token = jwt.JWT(header=header, claims=self.unencrypted)
        e_token.make_encrypted_token(key=self.encryption_key)
        self._encrypted = e_token.serialize()
        return self.tokens

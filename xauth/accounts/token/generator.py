import json

from django.utils.datetime_safe import datetime
from jwcrypto import jwt
from xently.core.loading import get_class

from xauth.internal_settings import TOKEN_EXPIRY, REQUEST_TOKEN_ENCRYPTED, AUTH_APP_LABEL

__all__ = ["Token"]


class Token(get_class(f"{AUTH_APP_LABEL}.token.key", "TokenKey")):
    def __init__(self, payload, activation_date=None, expiry_period=None, payload_key=None, subject=None):
        super().__init__()
        self._unencrypted = None
        self._encrypted = None
        self.subject = subject or "access"
        self.payload = payload
        self.payload_key = payload_key or "payload"
        self.activation_date = activation_date
        self.expiry_period = expiry_period

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
        issue_date = datetime.now()
        self.activation_date = issue_date if not self.activation_date else self.activation_date
        self.expiry_period = TOKEN_EXPIRY if self.expiry_period is None else self.expiry_period

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
        return {"unencrypted": self.unencrypted, "encrypted": self.encrypted}

    def get_claims(self, token=None, encrypted: bool = REQUEST_TOKEN_ENCRYPTED):
        token = self.encrypted if not token else token
        assert token is not None, "Call .refresh() first or provide a token"
        token = token.decode() if isinstance(token, bytes) else token
        try:
            token = jwt.JWT(key=self.encryption_key, jwt=f"{token}").claims if encrypted else token
        except ValueError:
            raise jwt.JWException
        return json.loads(jwt.JWT(key=self.get_jwt_signing_keys()[1], jwt=token).claims)

    def get_payload(self, token=None, encrypted: bool = REQUEST_TOKEN_ENCRYPTED):
        try:
            return self.get_claims(token, encrypted).get(self.payload_key, None)
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

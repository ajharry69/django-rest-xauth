import json
import os
from hashlib import md5
from pathlib import Path

from django.conf import settings
from django.utils.datetime_safe import datetime
from jwcrypto import jwk, jwt
from jwcrypto.common import json_decode

from xauth.internal_settings import *  # noqa

__all__ = ["JWT_SIG_ALG", "TokenKey", "Token"]

# JWT_SIG_ALG = 'HS256'
JWT_SIG_ALG = "RS256"


class TokenKey:
    ALLOWED_SIGNING_ALGORITHMS = ["RS256", "HS256"]

    # Create a folder in the root directory of the project to hold generated keys
    # This directory should not be committed to version control
    KEYS_ROOT_PATH = str(getattr(settings, "XAUTH_KEYS_DIR", Path(settings.BASE_DIR).parent / ".secrets"))

    def __init__(self, password=settings.SECRET_KEY, signing_algorithm=JWT_SIG_ALG):
        self.password = password.encode()
        assert (
            signing_algorithm in self.__class__.ALLOWED_SIGNING_ALGORITHMS
        ), f"{signing_algorithm} must be one of {self.__class__.ALLOWED_SIGNING_ALGORITHMS}"
        self.signing_algorithm = signing_algorithm
        Path(self.KEYS_ROOT_PATH).mkdir(parents=True, exist_ok=True)

    @property
    def encryption_key(self):
        # Generate an encryption key...
        return self._get_jwt_signing_or_encryption_key(encryption=True)

    def _jwt_signing_keys(self):
        """
        Return a `JWK` key for `JWT` token encryption or a `tuple` of JWK keys for `JWT` token signing
        (`private` key, `public` key) depending on the signing algorithm used
        :return: `JWK` key or `tuple` of `JWKs` keys
        """

        if self.signing_algorithm == "HS256":
            # Default signing algorithm used when all else fails
            # `JWT` signing key
            try:
                with open(f"{self.KEYS_ROOT_PATH}/signing_key", "rb") as file:
                    jwt_sig_key = jwk.JWK(**json_decode(file.readline()))
            except FileNotFoundError:
                jwt_sig_key = jwk.JWK(generate="oct", size=256)
                with open(f"{self.KEYS_ROOT_PATH}/signing_key", "wb") as file:
                    file.write(jwt_sig_key.export().encode())

            # Public `JWT` signing key for `JWT` verification
            jwt_pub_sig_key = jwt_sig_key
            # Private `JWT` signing key for `JWT` signing
            jwt_pri_sig_key = jwt_sig_key
        else:
            # Private `JWT` signing key for `JWT` signing
            jwt_pri_sig_key = self._get_jwt_signing_or_encryption_key()
            # Public `JWT` signing key for `JWT` verification
            jwt_pub_sig_key = self._get_jwt_signing_or_encryption_key(False)

        # Use the same key(private) for **signing** and **verifying** keys...
        return jwt_pri_sig_key, jwt_pri_sig_key or jwt_pub_sig_key

    def _get_key_from_pem(self, file, private):
        with open(file, "rb") as pem:
            return jwk.JWK.from_pem(pem.read(), password=self.password if private else None)

    def _get_jwt_signing_or_encryption_key(self, private=True, encryption=False):
        """
        Creates a `private` signing or encryption key(s)

        :param private: `bool` to specifying if `key` is `private key`
        :return: `jwk.JWK` Encryption & signing key
        """

        file_name, key = self._get_signing_or_encryption_key_or_path(private, encryption)
        file_name = md5(file_name.encode(encoding="utf8", errors="replace")).hexdigest()
        file = os.path.join(self.KEYS_ROOT_PATH, f"{file_name}.pem")

        try:
            # get key from .pem file contents
            key = self._get_key_from_pem(file, private)
        except FileNotFoundError:
            with open(file, "wb") as pem:
                # Write the key's to .pem file
                pem.write(key.export_to_pem(private_key=private, password=self.password if private else None))
            key = self._get_key_from_pem(file, private)

        return key

    @staticmethod
    def _get_signing_or_encryption_key_or_path(private: bool, encryption: bool):
        if encryption:
            return "encryption_key", jwk.JWK.generate(kty="EC", alg="ECDH-ES", crv="P-256")

        file_name = "signing_key"
        key_op = "verify"  # `Public Key` will be used for `verifying` the `token`
        file_name += "_pub"  # `public` signing key `file name`
        if private:
            key_op = "sign"  # `Private Key` will be used for `signing` the `token`
            file_name += "_pri"  # `private` signing key `file name`
        return file_name, jwk.JWK.generate(kty="RSA", key_ops=key_op, alg="RSA-OAEP", size=2048)


class Token(TokenKey):
    def __init__(self, payload, activation_date=None, expiry_period=None, payload_key=None, subject=None):
        super().__init__(signing_algorithm=JWT_SIG_ALG)
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
        token = jwt.JWT(key=self.encryption_key, jwt=f"{token}").claims if encrypted else token
        return json.loads(jwt.JWT(key=self._jwt_signing_keys()[1], jwt=token).claims)

    def get_payload(self, token=None, encrypted: bool = REQUEST_TOKEN_ENCRYPTED):
        try:
            return self.get_claims(token, encrypted).get(self.payload_key, None)
        except AssertionError:
            return self.payload

    def refresh(self):
        header = {"alg": self.signing_algorithm, "typ": "JWT"}
        # unencrypted token
        token = jwt.JWT(header, self.claims, check_claims=self.checked_claims, algs=self.ALLOWED_SIGNING_ALGORITHMS)
        token.make_signed_token(key=self._jwt_signing_keys()[0])
        self._unencrypted = token.serialize()
        header = {"alg": "ECDH-ES", "enc": "A256GCM"}
        # encrypted token
        e_token = jwt.JWT(header=header, claims=self.unencrypted)
        e_token.make_encrypted_token(key=self.encryption_key)
        self._encrypted = e_token.serialize()
        return self.tokens

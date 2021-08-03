import os
from hashlib import md5
from pathlib import Path

from django.conf import settings
from jwcrypto import jwk
from jwcrypto.common import json_decode

from xauth.internal_settings import MAKE_KEY_DIRS, KEYS_DIR, JWT_SIG_ALG

__all__ = ["TokenKey"]


class TokenKey:
    ALLOWED_SIGNING_ALGORITHMS = ["RS256", "HS256"]

    def __init__(self, password=None, signing_algorithm=None):
        self.password = (password or settings.SECRET_KEY).encode()
        self.signing_algorithm = signing_algorithm or JWT_SIG_ALG
        assert (
            self.signing_algorithm in self.__class__.ALLOWED_SIGNING_ALGORITHMS
        ), f"{self.signing_algorithm} must be one of {self.__class__.ALLOWED_SIGNING_ALGORITHMS}"
        if MAKE_KEY_DIRS:
            Path(KEYS_DIR).mkdir(parents=True, exist_ok=True)

    def get_or_create_rs_256_key(self, file, key, is_private):
        password = self.password if is_private else None
        try:
            # get key from .pem file contents
            with open(file, "rb") as pem:
                key = jwk.JWK.from_pem(pem.read(), password=password)
        except FileNotFoundError:
            with open(file, "wb") as pem:
                # Write the key's to .pem file
                pem.write(key.export_to_pem(private_key=is_private, password=password))
        return key

    def get_or_create_hs_256_key(self, file, key):
        try:
            with open(file, "rb") as key_file:
                key = jwk.JWK(**json_decode(key_file.readline()))
        except FileNotFoundError:
            with open(file, "wb") as key_file:
                key_file.write(key.export().encode())
        return key

    def _get_jwt_signing_or_encryption_key(self, is_private=True, is_encryption=False):
        if is_encryption:
            file_name, key = "encryption_key", jwk.JWK.generate(kty="EC", alg="ECDH-ES", crv="P-256")
        else:
            file_name = "signing_key"
            key_op = "verify"  # `Public Key` will be used for `verifying` the `token`
            file_name += "_pub"  # `public` signing key `file name`
            if is_private:
                key_op = "sign"  # `Private Key` will be used for `signing` the `token`
                file_name += "_pri"  # `private` signing key `file name`
            key = jwk.JWK.generate(kty="RSA", key_ops=key_op, alg="RSA-OAEP", size=2048)

        file_name = md5(file_name.encode(encoding="utf8", errors="replace")).hexdigest()
        return self.get_or_create_rs_256_key(os.path.join(KEYS_DIR, f"{file_name}.pem"), key, is_private)

    @property
    def encryption_key(self):
        return self._get_jwt_signing_or_encryption_key(is_encryption=True)

    def get_jwt_signing_keys(self):
        """
        Return a `JWK` key for `JWT` token encryption or a `tuple` of JWK keys for `JWT` token signing
        (`private` key, `public` key) depending on the signing algorithm used
        :return: `JWK` key or `tuple` of `JWKs` keys
        """

        if self.signing_algorithm == "HS256":
            # Default signing algorithm used when all else fails.
            # `JWT` signing key
            jwt_sig_key = self.get_or_create_hs_256_key(
                Path(KEYS_DIR) / md5("signing_key".encode(encoding="utf8", errors="replace")).hexdigest(),
                jwk.JWK(generate="oct", size=256),
            )

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

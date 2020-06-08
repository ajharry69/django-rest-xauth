import json
import os

from django.utils.datetime_safe import datetime
from jwcrypto import jwk, jwt
from jwcrypto.common import json_decode

from xauth.utils.settings import *

# JWT_SIG_ALG = 'HS256'
JWT_SIG_ALG = 'RS256'


class TokenKey:
    """
    :param password: for wrapping the private signing and encryption key(s) generated during `.pem` file creation
    :param signing_algorithm: signing algorithm. Can either be 'RS256' or 'HS256'
    """
    ALLOWED_SIGNING_ALGORITHMS = ['RS256', 'HS256']

    # Create a folder in the root directory of the project to hold generated keys
    # This directory should not be committed to version control
    KEYS_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('/xauth', ''),
                                  'xauth-secrets')

    def __init__(self, password=settings.SECRET_KEY, signing_algorithm=JWT_SIG_ALG):
        self.password = password.encode()
        assert (signing_algorithm in self.ALLOWED_SIGNING_ALGORITHMS), \
            f'{signing_algorithm} must be in {self.ALLOWED_SIGNING_ALGORITHMS}'
        self.signing_algorithm = signing_algorithm

    @property
    def encryption_key(self):
        # Generate an encryption key...
        return self._get_jwt_signing_or_encryption_key(encryption=True)

    @property
    def private_signing_key(self):
        return self._jwt_signing_keys()[0]

    @property
    def public_signing_key(self):
        return self._jwt_signing_keys()[1]

    def _jwt_signing_keys(self):
        """
        Return a `JWK` key for `JWT` token encryption or a `tuple` of JWK keys for `JWT` token signing
        (`private` key, `public` key) depending on the signing algorithm used
        :return: `JWK` key or `tuple` of `JWKs` keys
        """

        if self.signing_algorithm == 'HS256':
            # Default signing algorithm used when all else fails
            # `JWT` signing key
            jwt_sig_key = self._get_default_signing_key()

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

    def _get_jwt_signing_or_encryption_key(self, private=True, encryption=False) -> jwk.JWK:
        """
        Creates a `private` signing or encryption key(s)

        :param private: `bool` to specifying if `key` is `private key`
        :return: `jwk.JWK` Encryption & signing key
        """

        file_name, path, key = self._get_signing_or_encryption_key_or_path(private, encryption)
        file = os.path.join(path, f'{file_name}_{datetime.now().year}.pem')

        try:
            self._make_dirs_if_not_exist(path)
            # get key from .pem file contents
            key = self._get_key_from_pem(file, private)
        except FileNotFoundError:
            # Key file not found! Create new
            key = self._create_pem_file(file, key, private)

        return key

    def _get_signing_or_encryption_key_or_path(self, private: bool, encryption: bool):
        path = self.KEYS_ROOT_PATH
        file_name = 'key'
        if encryption:
            path += '/enc'  # `Encryption` keys directory
            key = jwk.JWK.generate(kty='EC', alg='ECDH-ES', crv='P-256')
        else:
            path += '/sig'  # `Signing` keys directory
            file_name, key_op = self._get_key_op_and_filename_suffix(file_name, private)
            key = jwk.JWK.generate(kty='RSA', key_ops=key_op, alg='RSA-OAEP', size=2048)
        return file_name, path, key

    @staticmethod
    def _get_key_op_and_filename_suffix(file_name, private):
        if private:
            # `Private Key` will be used for `signing` the `token`
            op = 'sign'
            file_name += '_pri'  # `private` signing key `file name`
        else:
            # `Public Key` will be used for `verifying` the `token`
            op = 'verify'
            file_name += '_pub'  # `public` signing key `file name`
        return file_name, op

    @staticmethod
    def _make_dirs_if_not_exist(dirs):
        if not os.path.exists(dirs):
            # make the required directories if they don't exist
            os.makedirs(dirs)

    def _get_default_signing_key(self) -> jwk.JWK:
        """
        {"k":"VXijve0VHZY1*******IYwGDFTlo1s3PA","kty":"oct"}
        """
        try:
            self._make_dirs_if_not_exist(self.KEYS_ROOT_PATH)
            with open(f'{self.KEYS_ROOT_PATH}/signing_key.txt', 'rb') as file:
                return jwk.JWK(**json_decode(file.readline()))
        except FileNotFoundError:
            key = jwk.JWK(generate='oct', size=256)
            with open(f'{self.KEYS_ROOT_PATH}/signing_key.txt', 'wb') as file:
                file.write(key.export().encode())
            return key

    def _create_pem_file(self, file, key, private) -> jwk.JWK:
        with open(file, 'wb') as pem:
            # Write the key's to .pem file
            pem.write(key.export_to_pem(private_key=private, password=self.__password(private)))
        return self._get_key_from_pem(file, private)

    def _get_key_from_pem(self, file, private) -> jwk.JWK:
        """
        Reads a .pem file containing encryption or signing keys as generated by [jwk.JWK]
        :param file: `.pem` file that is to be read
        :return: jwk.JWK
        """
        with open(file, "rb") as pem:
            return jwk.JWK.from_pem(pem.read(), password=self.__password(private))

    def __password(self, private):
        return self.password if private else None


class Token(TokenKey):
    """
    :param payload will be added as a value with a key as `payload_key` as part of the `jwt.JWT` claims
    :param activation_date `datetime` when the generated token should be considered active/valid and ready for use.
    Defaults to the current `datetime` if an alternative is not provided
    :param expiry_period `datetime` when the generated token should be considered in[active/valid] and not usable.
    Defaults to 60days from `activation_date` if an alternative is not provided
    :param payload_key key for `payload` during claims generations
    """

    def __init__(self, payload, activation_date: datetime = None, expiry_period: timedelta = None,
                 payload_key: str = 'payload', signing_algorithm=JWT_SIG_ALG, subject=None, ):
        super().__init__(password=TOKEN_KEY, signing_algorithm=signing_algorithm)
        self._normal = None
        self._encrypted = None
        self.subject = subject if subject else 'access'
        self.payload = payload
        self.payload_key = payload_key
        self.activation_date = activation_date
        self.expiry_period = expiry_period

    def __str__(self):
        # self.__repr__() # makes sure
        return json.dumps(self.__dict__)

    def __repr__(self):
        return json.dumps(self.tokens)

    @property
    def normal(self):
        """
        :return: unencrypted token
        """
        if self._normal is None:
            self.refresh()
        return self._normal

    @property
    def encrypted(self):
        """
        :return: encrypted token
        """
        if self._encrypted is None:
            self.refresh()
        return self._encrypted

    @property
    def checked_claims(self):
        """
        Creates and returns a dictionary of `jwt.JWT` claims that will be checked for presence and validity
        """
        issue_date = datetime.now()
        self.activation_date = issue_date if not self.activation_date else self.activation_date
        self.expiry_period = TOKEN_EXPIRY if self.expiry_period is None else self.expiry_period

        expiry_date = self.activation_date + self.expiry_period
        activation_secs = int(self.activation_date.strftime('%s'))
        expiry_secs = int(expiry_date.strftime('%s'))
        assert (expiry_secs > activation_secs), 'Expiration date must be a date later than activation date'
        return {
            'nbf': activation_secs,
            'exp': expiry_secs,
            'iat': int(issue_date.strftime('%s')),
            'sub': self.subject,
        }

    @property
    def claims(self):
        """
        Creates and returns a dictionary of `jwt.JWT` claims that is a combination of `checked_claims` and the `payload`
        """
        # convert provided payload to string if it is not already a string or a dictionary
        # self.payload = str(self.payload) if not isinstance(self.payload, dict) else self.payload
        cc = self.checked_claims
        cc[self.payload_key] = self.payload
        return cc

    @property
    def tokens(self):
        if not self.normal or not self.encrypted:
            self.refresh()
        return dict(normal=self.normal, encrypted=self.encrypted)

    def get_claims(self, token=None, encrypted: bool = REQUEST_TOKEN_ENCRYPTED):
        token = self.encrypted if not token else token
        assert token is not None, "Call refresh() first or provide a token"
        token = token.decode() if isinstance(token, bytes) else token
        tk = jwt.JWT(key=self.encryption_key, jwt=u"%s" % token).claims if encrypted else token
        claims = jwt.JWT(key=self.public_signing_key, jwt=tk).claims
        return json.loads(claims)

    def get_payload(self, token=None, encrypted: bool = REQUEST_TOKEN_ENCRYPTED):
        try:
            return self.get_claims(token, encrypted).get(self.payload_key, None)
        except AssertionError:
            return self.payload

    def refresh(self):
        header = {
            'alg': self.signing_algorithm,
            'typ': 'JWT',
        }
        # normal(unencrypted) token
        token = jwt.JWT(header=header, claims=self.claims, check_claims=self.checked_claims,
                        algs=self.ALLOWED_SIGNING_ALGORITHMS)
        token.make_signed_token(key=self.private_signing_key)
        self._normal = token.serialize()
        header = {
            'alg': "ECDH-ES",
            'enc': "A256GCM",
        }
        # header = XAUTH.get('JWT_ENC_HEADERS', {
        #     "alg": "A256KW",
        #     "enc": "A256CBC-HS512",
        # })
        # encrypted token
        e_token = jwt.JWT(header=header, claims=self.normal)
        e_token.make_encrypted_token(key=self.encryption_key)
        self._encrypted = e_token.serialize()
        return self.tokens

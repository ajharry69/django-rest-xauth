from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase

from xauth import authentication


class BasicTokenAuthenticationTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username='user',
            email='user@mail-domain.com',
            password='password',
        )
        self.backend = authentication.BasicTokenAuthentication()

    def test_get_user_with_correct_username_and_password(self):
        user = self.backend.get_user_with_username_and_password(username='user', password='password')
        self.assertIsNotNone(user)
        self.assertEqual(self.user, user)

    def test_get_user_with_correct_username_and_wrong_password(self):
        with self.assertRaises(AuthenticationFailed):
            user = self.backend.get_user_with_username_and_password(username='user', password='password1')

    def test_get_user_with_incorrect_username_and_password(self):
        with self.assertRaises(AuthenticationFailed):
            user = self.backend.get_user_with_username_and_password(username='user1', password='password')

    def test_get_user_with_None_username_and_None_password(self):
        user = self.backend.get_user_with_username_and_password(username=None, password=None)
        self.assertIsNone(user)

    def test_get_basic_auth_username_and_password(self):
        from requests.auth import _basic_auth_str
        _username, _password = 'user', 'password'
        credentials = _basic_auth_str(_username, _password).split()[1]
        username, password = self.backend.get_basic_auth_username_and_password(credentials)
        self.assertEqual(username, _username)
        self.assertEqual(password, _password)

    def test_get_client_ip_with_comma_separated_addresses(self):
        addresses_str = '127.0 .0.1, 10.0.2.2,  125.25.32.12'
        self.assertEqual(self.backend.get_client_ip(addresses_str), '127.0.0.1')

    def test_get_client_ip_with_one_address(self):
        addresses_str = '127.0 .0.1,'
        addresses_str_1 = ',127.0 .0.1'
        addresses_str_2 = ',127.0 .0.1,'
        self.assertEqual(self.backend.get_client_ip(addresses_str), '127.0.0.1')
        self.assertEqual(self.backend.get_client_ip(addresses_str_1), '127.0.0.1')
        self.assertEqual(self.backend.get_client_ip(addresses_str_2), '127.0.0.1')

    def test_get_client_ip_with_None_address(self):
        addresses_str = None
        self.assertEqual(self.backend.get_client_ip(addresses_str), None)

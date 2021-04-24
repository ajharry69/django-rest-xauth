from django.urls import reverse
from rest_framework import status

from tests import *  # noqa


class SignInViewTestCase(APITestCase):
    def assert_post_request_auth(self, _username, _password, expect_status_code, expect_null_payload: bool = True):
        response = self.client.post(
            reverse("xauth:signin"),
            data={
                "username": _username,
                "password": _password,
            },
        )
        self.assertEqual(response.status_code, expect_status_code)
        self.assertIsNotNone(
            get_response_data_message(response) if expect_null_payload else get_response_data_payload(response)
        )
        return response

    def assert_basic_auth(self, _username, _password, expect_status_code, expect_null_payload: bool = True):
        from requests.auth import _basic_auth_str

        self.client.credentials(HTTP_AUTHORIZATION=_basic_auth_str(_username, _password))
        response = self.client.post(
            reverse("xauth:signin"),
        )
        self.assertEqual(response.status_code, expect_status_code)
        self.assertIsNotNone(
            get_response_data_message(response) if expect_null_payload else get_response_data_payload(response)
        )
        return response

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user",
            email="user@mail-domain.com",
            password="password",
        )

    def test_signing_in_with_valid_basic_authentication_credentials_returns_200(self):
        self.assert_basic_auth("user", "password", status.HTTP_200_OK, False)

    def test_signing_in_with_invalid_basic_authentication_username_returns_401(self):
        self.assert_basic_auth("user1", "password", status.HTTP_401_UNAUTHORIZED)

    def test_signing_in_with_invalid_basic_authentication_password_returns_401(self):
        self.assert_basic_auth("user", "password1", status.HTTP_401_UNAUTHORIZED)

    def test_signing_in_with_invalid_basic_authentication_username_and_password_returns_401(self):
        self.assert_basic_auth("user1", "password1", status.HTTP_401_UNAUTHORIZED)

    def test_signing_in_with_valid_post_request_credentials_returns_200(self):
        """credentials mean: value contained in username & password fields of a POST request"""
        self.assert_post_request_auth("user", "password", status.HTTP_200_OK, False)

    def test_signing_in_with_invalid_post_request_username_returns_401(self):
        self.assert_post_request_auth("user1", "password", status.HTTP_401_UNAUTHORIZED)

    def test_signing_in_with_invalid_post_request_password_returns_401(self):
        self.assert_post_request_auth("user", "password1", status.HTTP_401_UNAUTHORIZED)

    def test_signing_in_with_invalid_post_request_username_and_password_returns_401(self):
        self.assert_post_request_auth("user1", "password1", status.HTTP_401_UNAUTHORIZED)

    def test_sign_in_to_inactive_account_returns_401(self):
        self.user.is_active = False
        self.user.save()
        response = self.assert_basic_auth("user", "password", status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(get_response_data_message(response), "account was deactivated")

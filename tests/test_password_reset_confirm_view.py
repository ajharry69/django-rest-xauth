from rest_framework import status
from rest_framework.reverse import reverse

from tests import *  # noqa


class PasswordResetConfirmViewTestCase(ChangeConfirmationAPITestCase):
    def add_authorization_header(self, auth_data):
        self.client.credentials(HTTP_AUTHORIZATION=auth_data)

    def assert_invalid_authentication_data_or_scheme(self, auth_data):
        self.add_authorization_header(auth_data)
        response, _, _ = self.request_password_reset()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(get_response_data_message(response), "Authentication credentials were not provided.")

    def request_password_reset(self):
        token, correct_temporary_password = self.user.request_password_reset(send_mail=False)
        new_password = "new_password"
        self.assertIs(self.user.check_password(self.password), True)
        self.user.is_verified = True  # without this token expiry test would fail
        self.user.save()
        self.assertIs(self.user.check_password(self.password), True)
        response = self.client.post(
            reverse("xauth:password-reset-confirm"),
            data={
                "temporary_password": correct_temporary_password,
                "new_password": new_password,
            },
        )
        return response, new_password, token

    def request_successful_password_reset(self, auth_token):
        self.add_authorization_header(f"Bearer {auth_token.encrypted}")
        return self.request_password_reset()

    def assert_invalid_authentication_token(self, auth_token, debug_message):
        response, _, _ = self.request_successful_password_reset(auth_token)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(get_response_data_message(response), "invalid token")
        self.assertEqual(get_response_data_debug_message(response), debug_message)

    def test_reset_password_with_correct_temporary_password_returns_200(self):
        auth_token = self.user.password_reset_token
        response, new_password, token = self.request_successful_password_reset(auth_token)

        token_expiry_days, user = self.code_password_verification(response, token)
        self.assertIs(user.check_password(new_password), True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # token expiry is closer to 60days
        self.assertIn(token_expiry_days, range(58, 62))

    def test_reset_password_with_incorrect_temporary_password_returns_400(self):
        token, correct_temporary_password = self.user.request_password_reset(send_mail=False)
        auth_token = self.user.password_reset_token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = self.client.post(
            reverse("xauth:password-reset-confirm"),
            data={
                "temporary_password": "wrong_temporary_password",
                "new_password": "new_password",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_response_data_message(response), "incorrect")

    def test_verifying_account_with_verification_token_returns_401(self):
        auth_token, debug_message = self.user.verification_token, "tokens is restricted to verification"

        self.assert_invalid_authentication_token(auth_token, debug_message)

    def test_verifying_account_with_activation_token_returns_401(self):
        auth_token, debug_message = self.user.activation_token, "tokens is restricted to activation"

        self.assert_invalid_authentication_token(auth_token, debug_message)

    def test_resetting_password_with_an_invalid_authentication_scheme_returns_401(self):
        self.assert_invalid_authentication_data_or_scheme(f"UnknownScheme {self.user.password_reset_token.encrypted}")

    def test_resetting_password_with_an_invalid_authentication_data_returns_401(self):
        # no space between authentication scheme and authentication data
        self.assert_invalid_authentication_data_or_scheme(f"Bearer{self.user.password_reset_token.encrypted}")

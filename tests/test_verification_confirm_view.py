from rest_framework import status
from rest_framework.reverse import reverse

from tests import *  # noqa


class VerificationConfirmViewTestCase(ChangeConfirmationAPITestCase):
    def assert_invalid_authentication_token(self, auth_token, debug_message):
        _, correct_code = self.user.request_verification(send_mail=False)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token.encrypted}")
        response = self.client.post(
            reverse("xauth:verification-confirm"),
            data={"code": correct_code},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(get_response_data_message(response), "invalid token")
        self.assertEqual(get_response_data_debug_message(response), debug_message)

    def test_verification_with_correct_code_returns_200(self):
        verification_token = self.user.token.encrypted
        token, correct_code = self.user.request_verification(send_mail=False)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {verification_token}")
        response = self.client.post(reverse("xauth:verification-confirm"), data={"code": correct_code})

        token_expiry_days, user = self.code_password_verification(response, token)

        self.assertIs(user.is_verified, True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # token expiry is closer to 60days
        self.assertIn(token_expiry_days, range(58, 62))

    def test_verification_with_incorrect_code_returns_400(self):
        verification_token = self.user.token.encrypted
        _, correct_code = self.user.request_verification(send_mail=False)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {verification_token}")
        response = self.client.post(
            reverse("xauth:verification-confirm"),
            data={"code": "123456"},  # should be wrong! 1 is not expected to be part of generated code
        )

        user = get_user_model().objects.get_by_natural_key(self.user.username)

        self.assertIs(user.is_verified, False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_response_data_message(response), "incorrect")

    def test_verifying_account_with_password_reset_token_returns_401(self):
        auth_token, debug_message = self.user.password_reset_token, "tokens is restricted to password-reset"

        self.assert_invalid_authentication_token(auth_token, debug_message)

    def test_verifying_account_with_activation_token_returns_401(self):
        auth_token, debug_message = self.user.activation_token, "tokens is restricted to activation"

        self.assert_invalid_authentication_token(auth_token, debug_message)

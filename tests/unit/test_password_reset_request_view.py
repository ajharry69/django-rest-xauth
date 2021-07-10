from rest_framework import status
from rest_framework.reverse import reverse

from tests.testcases import *  # noqa


class PasswordResetRequestViewTestCase(UserAPITestCase):
    def test_request_password_reset_with_valid_authorization_returns_200(self):
        pr_token = self.user.password_reset_token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {pr_token}")
        response = self.client.post(
            reverse("xauth:password-reset-request"),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(get_response_data_payload(response))

    def test_request_password_reset_with_registered_email_returns_200(self):
        """assumes no other authentication schemes were found in the headers"""
        self.client.credentials()
        response = self.client.post(reverse("xauth:password-reset-request"), data={"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(get_response_data_payload(response))

    def test_request_password_reset_with_unregistered_email_returns_404(self):
        """assumes no other authentication schemes were found in the headers"""
        self.client.credentials()
        response = self.client.post(
            reverse("xauth:password-reset-request"), data={"email": "self.user.email@mail-domain.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(get_response_data_message(response), "email address is not registered")

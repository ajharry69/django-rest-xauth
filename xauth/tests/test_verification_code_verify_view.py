from rest_framework import status
from rest_framework.reverse import reverse

from xauth.tests import *


class VerificationCodeVerifyViewTestCase(CodeVerificationAPITestCase):
    def test_verification_with_correct_code_returns_200(self):
        token, correct_code = self.user.request_verification(send_mail=False)
        verification_token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {verification_token}')
        response = self.client.post(reverse('xauth:verification-code-verify'), data={
            'code': correct_code
        })

        token_expiry_days, user = self.code_password_verification(response, token)

        self.assertIs(user.is_verified, True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # token expiry is closer to 60days
        self.assertIn(token_expiry_days, range(58, 62))

    def test_verification_with_incorrect_code_returns_400(self):
        verification_token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {verification_token}')
        response = self.client.post(reverse('xauth:verification-code-verify'), data={
            'code': '123456'  # should be wrong! 1 is not expected to be part of generated code
        }, )

        user = get_user_model().objects.get_by_natural_key(self.user.username)

        self.assertIs(user.is_verified, False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message', None), 'incorrect')

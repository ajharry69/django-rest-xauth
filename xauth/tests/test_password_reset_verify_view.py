from rest_framework import status
from rest_framework.reverse import reverse

from xauth.tests import *


class PasswordResetVerifyViewTestCase(CodeVerificationAPITestCase):

    def test_reset_password_with_correct_temporary_password_returns_200(self):
        token, correct_temporary_password = self.user.request_password_reset(send_mail=False)
        new_password = 'new_password'
        self.assertIs(self.user.check_password(self.password), True)
        self.user.is_verified = True  # without this token expiry test would fail
        self.user.save(auto_hash_password=False, )
        self.assertIs(self.user.check_password(self.password), True)
        pr_token = self.user.password_reset_token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {pr_token}')
        response = self.client.post(reverse('xauth:password-reset-verify'), data={
            'temporary_password': correct_temporary_password,
            'new_password': new_password,
        })

        token_expiry_days, user = self.code_password_verification(response, token)
        self.assertIs(user.check_password(new_password), True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # token expiry is closer to 60days
        self.assertIn(token_expiry_days, range(58, 62))

    def test_reset_password_with_incorrect_temporary_password_returns_400(self):
        token, correct_temporary_password = self.user.request_password_reset(send_mail=False)
        pr_token = self.user.password_reset_token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {pr_token}')
        response = self.client.post(reverse('xauth:password-reset-verify'), data={
            'temporary_password': 'wrong_temporary_password',
            'new_password': 'new_password',
        }, )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message', None), 'incorrect')

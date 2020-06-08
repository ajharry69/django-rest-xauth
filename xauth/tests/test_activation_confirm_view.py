from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

from xauth.tests import *


@override_settings(XAUTH={'WRAP_DRF_RESPONSE': True, }, )
class ActivationConfirmViewTestCase(SecurityQuestionAPITestCase):

    def assert_invalid_authentication_token(self, auth_token, debug_message):
        _, correct_code = self.user.request_verification(send_mail=False)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token.encrypted}')
        response = self.client.post(reverse('xauth:activation-confirm'), data={
            'answer': self.correct_security_question_answer,
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(get_response_data_message(response), 'invalid token')
        self.assertEqual(get_response_data_debug_message(response), debug_message)

    def setUp(self) -> None:
        super().setUp()
        self.user.is_active = False
        self.user.save()
        self.correct_security_question_answer = 'blue'
        update_metadata(self.user, self.security_question, self.correct_security_question_answer)

    def test_account_activation_with_correct_answer_returns_200(self):
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('xauth:activation-confirm'), data={
            'answer': self.correct_security_question_answer,
        })

        user = get_user_model().objects.get_by_natural_key(self.user.username)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # account was successfully activated
        self.assertIs(user.is_active, True)

    def test_account_activation_with_incorrect_answer_returns_400(self):
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('xauth:activation-confirm'), data={
            'answer': 'yellow',
        }, )

        user = get_user_model().objects.get_by_natural_key(self.user.username)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_response_data_message(response), 'incorrect')
        self.assertIs(user.is_active, False)

    def test_verifying_account_with_verification_token_returns_401(self):
        auth_token, debug_message = self.user.verification_token, 'tokens is restricted to verification'

        self.assert_invalid_authentication_token(auth_token, debug_message)

    def test_verifying_account_with_password_reset_token_returns_401(self):
        auth_token, debug_message = self.user.password_reset_token, 'tokens is restricted to password-reset'

        self.assert_invalid_authentication_token(auth_token, debug_message)

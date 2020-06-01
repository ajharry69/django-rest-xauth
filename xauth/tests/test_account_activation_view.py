from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

from xauth.tests import *


@override_settings(XAUTH={'WRAP_DRF_RESPONSE': True, }, )
class AccountActivationViewTestCase(SecurityQuestionAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.user.is_active = False
        self.user.save(auto_hash_password=False)
        self.correct_security_question_answer = 'blue'
        update_metadata(self.user, self.security_question, self.correct_security_question_answer)

    def test_account_activation_with_correct_answer_returns_200(self):
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('xauth:activation-activate'), data={
            'answer': self.correct_security_question_answer,
        })

        user = get_user_model().objects.get_by_natural_key(self.user.username)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # account was successfully activated
        self.assertIs(user.is_active, True)

    def test_account_activation_with_incorrect_answer_returns_400(self):
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('xauth:activation-activate'), data={
            'answer': 'yellow',
        }, )

        user = get_user_model().objects.get_by_natural_key(self.user.username)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message', None), 'incorrect')
        self.assertIs(user.is_active, False)

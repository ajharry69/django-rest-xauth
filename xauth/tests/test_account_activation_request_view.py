from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

from xauth.tests import *


@override_settings(XAUTH={'WRAP_DRF_RESPONSE': True, }, )
class AccountActivationRequestViewTestCase(SecurityQuestionAPITestCase):

    def assert_correct_username_response(self, user, activation_methods):
        response = self.client.post(reverse('xauth:activation-request'), data={
            'username': user.username,
        }, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('metadata', None), activation_methods)

    def test_request_account_activation_with_registered_username_and_unusable_security_question_returns_200(self):
        """user has an invalid(not usable) security question attached"""
        activation_methods = ['creation_date']
        user = self.user
        self.assert_correct_username_response(user, activation_methods)

    def test_request_account_activation_with_registered_username_and_usable_security_question_returns_200(self):
        """user has an valid(usable) security question attached"""
        activation_methods = ['creation_date', 'security_question']
        user = self.user
        # attaches a usable security question to user instance
        update_metadata(user, self.security_question, 'blue')
        self.assert_correct_username_response(user, activation_methods)

    def test_request_account_activation_with_unregistered_username_returns_404(self):
        response = self.client.post(reverse('xauth:activation-request'), data={
            'username': 'self.user.username',  # unregistered username
        }, )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('message', None), 'username or email address is not registered')

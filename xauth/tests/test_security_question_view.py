from rest_framework import status
from rest_framework.reverse import reverse

from xauth.tests import *


class SecurityQuestionViewTestCase(UserAPITestCase):
    def setUp(self) -> None:
        self.security_question = create_security_question()
        super(SecurityQuestionViewTestCase, self).setUp()

    def test_GET_security_questions_is_permitted_without_authentication(self):
        self.client.credentials()
        response = self.client.get(reverse('xauth:securityquestion-list'), )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsafe_request_methods_are_not_permitted_without_authentication(self):
        """unsafe methods include POST,PUT,DELETE"""
        self.client.credentials()
        response = self.client.post(reverse('xauth:securityquestion-list'), data={
            'question': 'What was the name of your high school?',
        }, )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unsafe_request_methods_are_not_permitted_for_non_superuser(self):
        """unsafe methods include POST,PUT,DELETE"""
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('xauth:securityquestion-list'), data={
            'question': 'What was the name of your high school?',
        }, )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unsafe_request_methods_are_permitted_for_superuser(self):
        """unsafe methods include POST,PUT,DELETE"""
        token = self.superuser.token.encrypted
        question = 'What was the name of your high school?'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('xauth:securityquestion-list'), data={
            'question': question,
        }, )

        response_get = self.client.get(reverse('xauth:securityquestion-list'), )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # question is by default usable
        self.assertEqual(response.data.get('usable', False), True)
        self.assertEqual(response.data.get('question', None), question)
        # one created here + the other created during setup
        # "results" is used because pagination is enable for the project
        self.assertEqual(len(response_get.data.get('results')), 2)

    def test_DELETE_security_question_returns_204(self):
        token = self.superuser.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('xauth:securityquestion-detail', args=(self.security_question.id,), ), )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

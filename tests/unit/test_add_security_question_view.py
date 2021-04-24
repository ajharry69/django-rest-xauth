from rest_framework import status
from rest_framework.reverse import reverse

from tests import *  # noqa


class AddSecurityQuestionViewTestCase(SecurityQuestionAPITestCase):
    def assert_400_error_response(self, answer, error_response, question_id):
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(
            reverse("xauth:security-question-add"),
            data={
                "answer": answer,
                "question": question_id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_response_data_message(response), error_response)

    def test_given_a_valid_question_and_a_non_null_answer_returns_200(self):
        question = self.security_question
        token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(
            reverse("xauth:security-question-add"),
            data={
                "answer": "blue",
                "question": question.id,
            },
        )
        metadata = Metadata.objects.get(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(metadata.security_question.id, question.id)

    def test_given_invalid_question_returns_400(self):
        question_id, answer, error_response = -int(self.security_question.id), "blue", "invalid question"
        self.assert_400_error_response(answer, error_response, question_id)

    def test_given_invalid_answer_returns_400(self):
        """invalid answer means null/None answer"""
        question_id, answer, error_response = int(self.security_question.id), None, "invalid answer"
        self.assert_400_error_response(answer, error_response, question_id)

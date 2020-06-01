from xauth.tests import *


class SecurityQuestionTestCase(APITestCase):

    def setUp(self) -> None:
        self.security_question = create_security_question()

    def test_security_question_string_conversion(self):
        self.assertEqual(str(self.security_question), self.security_question.question)

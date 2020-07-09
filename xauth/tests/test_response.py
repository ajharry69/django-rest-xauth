from rest_framework.test import APITestCase

from xauth.utils.response import ErrorResponse


class APIResponseTestCase(APITestCase):
    def test_base_response_is_a_dictionary(self):
        response = ErrorResponse()
        self.assertIsInstance(response.data, dict)

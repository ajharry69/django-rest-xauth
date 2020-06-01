from rest_framework.test import APITestCase

from xauth.utils.response import APIResponse


class APIResponseTestCase(APITestCase):

    def test_is_error_default_matches(self):
        response = APIResponse()
        response.status_code = 200
        self.assertEqual(response.is_error, False)

    def test_message_default_matches(self):
        response = APIResponse()
        self.assertEqual(response.message, None)
        self.assertIsNone(response.message)

    def test_debug_message_default_matches(self):
        response = APIResponse()
        self.assertEqual(response.debug_message, None)
        self.assertIsNone(response.debug_message)

    def test_payload_default_matches(self):
        response = APIResponse()
        self.assertEqual(response.payload, None)
        self.assertIsNone(response.payload)

    def test_null_message_is_removed_from_base_response(self):
        response = APIResponse()
        self.assertNotIn('message', response.response(), "Message removed from base_response")

    def test_null_debug_message_is_removed_from_base_response(self):
        response = APIResponse()
        self.assertNotIn('debug_message', response.response(), "Debug message removed from base_response")

    def test_null_payload_is_removed_from_base_response(self):
        response = APIResponse()
        self.assertNotIn('payload', response.response(), "Payload removed from base_response")

    def test_is_error_always_present_in_base_response(self):
        response = APIResponse()
        self.assertIn('is_error', response.response(), "Is Error always present in base_response")

    def test_base_response_is_a_dictionary(self):
        response = APIResponse()
        self.assertIsInstance(response.response(), dict)

    def test_base_response_is_never_empty(self):
        response = APIResponse()
        self.assertDictEqual(response.response(), {'is_error': False, 'status_code': 200})

    def test_default_constructor_parameterized_client_api_response_equal_default(self):
        response = APIResponse()
        response_parameterized = APIResponse(None, None, None, True)
        self.assertDictEqual(response.response(), response_parameterized.__repr__())

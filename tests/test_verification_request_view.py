from rest_framework import status
from rest_framework.reverse import reverse

from tests import *


class VerificationRequestViewTestCase(UserAPITestCase):
    def test_request_verification_code_with_valid_authorized_returns_200(self):
        verification_token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {verification_token}')
        response = self.client.post(reverse('xauth:verification-request'), )

        user = get_user_model().objects.get_by_natural_key(self.user.username)
        self.assertIs(user.is_verified, False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

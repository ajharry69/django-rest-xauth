from rest_framework import status
from rest_framework.reverse import reverse

from xauth.models import AccessLog
from xauth.tests import *


class SignOutViewTestCase(UserAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()

    def test_signout_without_authentication_returns_200(self):
        response = self.client.post(reverse('xauth:signout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signout_with_authentication_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.token.encrypted}')
        response = self.client.post(reverse('xauth:signout'))

        access_log = AccessLog.objects.filter(user=self.user, sign_out_time__isnull=False).order_by(
            '-sign_out_time').first()
        signout_date = access_log.sign_out_time.date()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(signout_date == timezone.now().date(), True)

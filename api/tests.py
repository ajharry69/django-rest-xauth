from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class ApiRootViewTestCase(APITestCase):
    def test_root_api_returns_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

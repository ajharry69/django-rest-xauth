import base64

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tests.factories import UserFactory


class TestAccountViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.username = self.email = self.user.email
        self.password = "xauth54321"

    def test_signup(self):
        response = self.client.post(
            path=reverse("account-signup"),
            data={
                "email": "user@example.com",
                "password": "PVs5w()r9!",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert get_user_model().objects.filter(email="user@example.com").exists()
        assert "password" not in response.data
        assert isinstance(response.data["token"], dict)

    def test_signin_without_user_credentials(self):
        response = self.client.post(path=reverse("account-signin"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_signin_with_correct_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("account-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data["token"], dict)

    def test_signin_with_incorrect_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321-invalid", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("account-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

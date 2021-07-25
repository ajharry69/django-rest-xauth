import base64

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tests.factories import UserFactory


class TestAccountViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=True)
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

    def test_signin_to_unverified_account(self):
        user = UserFactory(is_verified=False)
        credentials = base64.b64encode(bytes(f"{user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("account-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert user == response.wsgi_request.user
        assert response.wsgi_request.user.token.subject == "verification"

    def test_signin_to_verified_account(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("account-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert self.user == response.wsgi_request.user
        assert response.wsgi_request.user.token.subject == "access"

    def test_signin_with_incorrect_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321-invalid", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("account-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_request_verification_code_requires_authentication(self):
        response = self.client.post(reverse("account-request-verification-code", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_request_verification_code_returns_verification_token(self):
        user = UserFactory(is_verified=False)
        self.client.force_login(user)
        response = self.client.get(reverse("account-request-verification-code", kwargs={"pk": user.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert user == response.wsgi_request.user
        assert response.wsgi_request.user.token.subject == "verification"

    def test_request_temporary_password_requires_authentication(self):
        response = self.client.post(reverse("account-request-temporary-password", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_request_temporary_password_returns_password_reset_token(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account-request-temporary-password", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert self.user == response.wsgi_request.user
        assert (
            response.wsgi_request.user.token.get_claims(response.data["token"]["encrypted"])["sub"] == "password-reset"
        )

    def test_get_user_profile_must_match_id_in_authorization_header_and_url_look_kwarg(self):
        user = UserFactory()
        self.client.force_login(self.user)
        response = self.client.get(reverse("account-detail", kwargs={"pk": user.pk}))

        assert user.pk != self.user.pk
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = self.client.get(reverse("account-detail", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_200_OK

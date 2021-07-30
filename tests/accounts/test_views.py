import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tests.factories import UserFactory, SecurityQuestionFactory


class TestAccountViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=True)
        self.username = self.email = self.user.email
        self.password = "xauth54321"
        assert self.user.check_password(self.password)

    def test_signup(self):
        response = self.client.post(
            path=reverse("user-signup"),
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
        response = self.client.post(path=reverse("user-signin"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_signin_with_correct_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data["token"], dict)

    def test_signin_to_unverified_account(self):
        user = UserFactory(is_verified=False)
        credentials = base64.b64encode(bytes(f"{user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert user == response.wsgi_request.user
        assert response.wsgi_request.user.token.subject == "verification"

    def test_signin_to_verified_account(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert self.user == response.wsgi_request.user
        assert response.wsgi_request.user.token.subject == "access"

    def test_signin_with_incorrect_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321-invalid", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_request_verification_code_requires_authentication(self):
        response = self.client.post(reverse("user-request-verification-code", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_request_verification_code_returns_verification_token(self):
        user = UserFactory(is_verified=False)
        self.client.force_login(user)
        response = self.client.get(reverse("user-request-verification-code", kwargs={"pk": user.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert user == response.wsgi_request.user
        assert response.wsgi_request.user.token.subject == "verification"

    def test_request_temporary_password_requires_authentication(self):
        response = self.client.post(reverse("user-request-temporary-password", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_request_temporary_password_returns_password_reset_token(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("user-request-temporary-password", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert self.user == response.wsgi_request.user
        assert (
            response.wsgi_request.user.token.get_claims(response.data["token"]["encrypted"])["sub"] == "password-reset"
        )

    def test_get_user_profile_must_match_id_in_authorization_header_and_url_look_kwarg(self):
        user = UserFactory()
        self.client.force_login(self.user)
        response = self.client.get(reverse("user-detail", kwargs={"pk": user.pk}))

        assert user.pk != self.user.pk
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = self.client.get(reverse("user-detail", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert "token" not in response.data

    def test_get_user_profile_with_bearer_token_authentication(self):
        response = self.client.get(
            path=reverse("user-detail", kwargs={"pk": self.user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.user.token.encrypted}",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.keys()) > 1
        assert "token" not in response.data

    def test_verify_account_with_invalid_code(self):
        user = UserFactory(is_verified=False)
        valid_code = user.request_verification()

        self.client.force_login(user)
        response = self.client.post(
            reverse("user-verify-account", kwargs={"pk": user.pk}), data={"code": "".join(reversed(valid_code))}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_account_with_valid_code(self):
        user = UserFactory(is_verified=False)
        valid_code = user.request_verification()

        self.client.force_login(user)
        response = self.client.post(reverse("user-verify-account", kwargs={"pk": user.pk}), data={"code": valid_code})

        assert response.status_code == status.HTTP_200_OK
        request_user = response.wsgi_request.user
        assert request_user.token.get_claims(response.data["token"]["encrypted"])["sub"] == "access"
        assert request_user.is_verified

    def test_reset_password_with_invalid_temporary_password(self):
        temporary_password = self.user.request_password_reset()

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": "".join(reversed(temporary_password)), "new_password": "PVs5w()r9!"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_with_invalid_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": "".join(reversed(self.password)), "new_password": "PVs5w()r9!", "is_change": True},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_with_valid_temporary_password(self):
        temporary_password = self.user.request_password_reset()

        assert self.user.check_password(self.password)

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": temporary_password, "new_password": "PVs5w()r9!"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.keys()) > 1
        assert "token" in response.data
        assert response.wsgi_request.user.check_password("PVs5w()r9!")

    def test_change_password_with_valid_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": self.password, "new_password": "PVs5w()r9!", "is_change": True},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.keys()) > 1
        assert "token" in response.data
        assert response.wsgi_request.user.check_password("PVs5w()r9!")

    def test_set_security_question_without_authentication_credentials(self):
        security_question = SecurityQuestionFactory()
        response = self.client.post(
            reverse("user-set-security-question", kwargs={"pk": self.user.pk}),
            data={
                "security_question": security_question.pk,
                "security_question_answer": "Transparent",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_set_security_question_with_authentication_credentials(self):
        security_question = SecurityQuestionFactory()

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-set-security-question", kwargs={"pk": self.user.pk}),
            data={
                "security_question": security_question.pk,
                "security_question_answer": "Transparent",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert self.user.security.security_question == security_question
        # Not stored without encryption
        assert self.user.security.security_question_answer != "Transparent"
        assert check_password("Transparent", self.user.security.security_question_answer)

    def test_activate_account_without_authentication_credentials(self):
        response = self.client.post(
            reverse("user-activate-account", kwargs={"pk": self.user.pk}),
            data={
                "security_question_answer": "answer",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_activate_account_with_authentication_credentials(self):
        self.client.force_login(self.user)
        with self.assertRaisesRegex(AttributeError, r".*models.UserActivationMixin.*"):
            self.client.post(
                reverse("user-activate-account", kwargs={"pk": self.user.pk}),
                data={
                    "security_question_answer": "answer",
                },
            )

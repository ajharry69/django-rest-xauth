import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tests.factories import UserFactory, SecurityQuestionFactory


class TestSecurityQuestionViewSet(APITestCase):
    def test_adding_security_question_without_staff_privilege(self):
        self.client.force_login(UserFactory())

        response = self.client.post(
            reverse("securityquestion-list"),
            data={
                "question": "What's your name?",
            },
        )

        assert response.status_code == 403

    def test_getting_security_question_without_staff_privilege(self):
        self.client.force_login(UserFactory())

        response = self.client.get(
            reverse("securityquestion-list"),
            data={
                "question": "What's your name?",
            },
        )

        assert response.status_code == 403

    def test_adding_security_question_with_staff_privilege(self):
        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.post(
            reverse("securityquestion-list"),
            data={
                "question": "What's your name?",
            },
        )

        assert response.status_code == 201

    def test_getting_security_question_with_staff_privilege(self):
        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get(
            reverse("securityquestion-list"),
            data={
                "question": "What's your name?",
            },
        )

        assert response.status_code == 200


class TestAccountViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=True)
        self.username = self.email = self.user.email
        self.password = "xauth54321"
        assert self.user.check_password(self.password)

    def test_signout_with_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("user-signout", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_200_OK

    def test_signout_with_unauthenticated_user(self):
        response = self.client.post(reverse("user-signout", kwargs={"pk": self.user.pk}))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_signup(self):
        response = self.client.post(
            path=reverse("user-signup"),
            data={
                "email": "user@example.com",
                "password": "PVs5w()r9!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.filter(email="user@example.com").get()
        self.assertNotIn("password", response.data)
        self.assertIsInstance(response.data["token"], dict)
        # Password should not be stored in plain text
        self.assertNotEqual(user.password, "PVs5w()r9!")
        self.assertTrue(user.check_password("PVs5w()r9!"))

    def test_password_not_required_during_user_detail_update(self):
        old_email = self.user.email
        self.client.force_login(self.user)
        response = self.client.put(
            reverse("user-detail", kwargs={"pk": self.user.pk}),
            data={
                "email": f"test.user{self.user.pk + 1}@example.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, old_email)
        self.assertNotIn("token", response.data)

    def test_password_not_required_during_user_detail_partial_update(self):
        old_email = self.user.email
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.user.pk}),
            data={
                "email": f"test.user{self.user.pk + 1}@example.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, old_email)
        self.assertNotIn("token", response.data)

    def test_signin_without_user_credentials(self):
        response = self.client.post(path=reverse("user-signin"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_signin_with_correct_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["token"], dict)

    def test_signin_to_unverified_account(self):
        user = UserFactory(is_verified=False)
        credentials = base64.b64encode(bytes(f"{user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(user, response.wsgi_request.user)
        self.assertEqual(response.wsgi_request.user.token.subject, "verification")

    def test_signin_to_verified_account(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(self.user, response.wsgi_request.user)
        self.assertEqual(response.wsgi_request.user.token.subject, "access")

    def test_signin_with_incorrect_basic_auth_credentials(self):
        credentials = base64.b64encode(bytes(f"{self.user.email}:xauth54321-invalid", encoding="utf8")).decode("utf8")
        response = self.client.post(path=reverse("user-signin"), HTTP_AUTHORIZATION=f"Basic {credentials}")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request_verification_code_requires_authentication(self):
        response = self.client.post(reverse("user-request-verification-code", kwargs={"pk": self.user.pk}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request_verification_code_returns_verification_token(self):
        user = UserFactory(is_verified=False)
        self.client.force_login(user)
        response = self.client.get(reverse("user-request-verification-code", kwargs={"pk": user.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        assert user == response.wsgi_request.user  # TODO: Use testcase's assertion methods
        self.assertEqual(response.wsgi_request.user.token.subject, "verification")

    def test_get_user_profile_must_match_id_in_authorization_header_and_url_look_kwarg(self):
        user = UserFactory()
        self.client.force_login(self.user)
        response = self.client.get(reverse("user-detail", kwargs={"pk": user.pk}))

        self.assertNotEqual(user.pk, self.user.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(reverse("user-detail", kwargs={"pk": self.user.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("token", response.data)

    def test_get_user_profile_with_encrypted_bearer_token_authentication(self):
        response = self.client.get(
            path=reverse("user-detail", kwargs={"pk": self.user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.user.token.encrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data.keys()), 1)
        self.assertNotIn("token", response.data)

    @override_settings(XAUTH_VERIFY_ENCRYPTED_TOKEN=False)
    def test_get_user_profile_with_expected_unencrypted_bearer_token_authentication(self):
        response = self.client.get(
            path=reverse("user-detail", kwargs={"pk": self.user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.user.token.unencrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_profile_with_unexpected_unencrypted_bearer_token_authentication(self):
        response = self.client.get(
            path=reverse("user-detail", kwargs={"pk": self.user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.user.token.unencrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_with_non_access_bearer_token_authentication(self):
        response = self.client.get(
            path=reverse("user-detail", kwargs={"pk": self.user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.user._password_reset_token.encrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid token")

    def test_verify_account_with_verification_bearer_token_authentication(self):
        user = UserFactory(is_verified=False)
        valid_code = user.request_verification()

        response = self.client.post(
            reverse("user-verify-account", kwargs={"pk": user.pk}),
            data={"code": valid_code},
            HTTP_AUTHORIZATION=f"Bearer {user.token.encrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_user = response.wsgi_request.user
        self.assertEqual(request_user.token.get_claims(response.data["token"]["encrypted"])["sub"], "access")
        self.assertTrue(request_user.is_verified)

    def test_verify_account_with_non_verification_bearer_token_authentication(self):
        user = UserFactory(is_verified=False)
        valid_code = user.request_verification()

        response = self.client.post(
            reverse("user-verify-account", kwargs={"pk": user.pk}),
            data={"code": valid_code},
            HTTP_AUTHORIZATION=f"Bearer {user._password_reset_token.encrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid token")

    def test_verify_account_with_invalid_code(self):
        user = UserFactory(is_verified=False)
        valid_code = user.request_verification()

        self.client.force_login(user)
        response = self.client.post(
            reverse("user-verify-account", kwargs={"pk": user.pk}), data={"code": "".join(reversed(valid_code))}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_account_with_valid_code(self):
        user = UserFactory(is_verified=False)
        valid_code = user.request_verification()

        self.client.force_login(user)
        response = self.client.post(reverse("user-verify-account", kwargs={"pk": user.pk}), data={"code": valid_code})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_user = response.wsgi_request.user
        self.assertEqual(request_user.token.get_claims(response.data["token"]["encrypted"])["sub"], "access")
        self.assertTrue(request_user.is_verified)

    def test_reset_password_with_invalid_temporary_password(self):
        temporary_password = self.user.request_password_reset()

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": "".join(reversed(temporary_password)), "new_password": "PVs5w()r9!"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_invalid_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": "".join(reversed(self.password)), "new_password": "PVs5w()r9!", "is_change": True},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_valid_temporary_password(self):
        temporary_password = self.user.request_password_reset()

        assert self.user.check_password(self.password)

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": temporary_password, "new_password": "PVs5w()r9!"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data.keys()), 1)
        self.assertIn("token", response.data)
        self.assertTrue(response.wsgi_request.user.check_password("PVs5w()r9!"))

    def test_change_password_with_valid_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user-reset-password", kwargs={"pk": self.user.pk}),
            data={"old_password": self.password, "new_password": "PVs5w()r9!", "is_change": True},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data.keys()), 1)
        self.assertIn("token", response.data)
        self.assertTrue(response.wsgi_request.user.check_password("PVs5w()r9!"))

    def test_set_security_question_without_authentication_credentials(self):
        security_question = SecurityQuestionFactory()
        response = self.client.post(
            reverse("user-set-security-question", kwargs={"pk": self.user.pk}),
            data={
                "security_question": security_question.pk,
                "security_question_answer": "Transparent",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.security.security_question, security_question)
        # Not stored in plain text
        self.assertNotEqual(self.user.security.security_question_answer, "Transparent")
        self.assertTrue(check_password("Transparent", self.user.security.security_question_answer))

    def test_activate_account_without_authentication_credentials(self):
        response = self.client.post(
            reverse("user-activate-account", kwargs={"pk": self.user.pk}),
            data={
                "security_question_answer": "answer",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_activate_account_with_authentication_credentials(self):
        self.client.force_login(self.user)
        with self.assertRaisesRegex(AttributeError, r".*models.UserActivationMixin.*"):
            self.client.post(
                reverse("user-activate-account", kwargs={"pk": self.user.pk}),
                data={
                    "security_question_answer": "answer",
                },
            )

    def test_requesting_verification_code_with_non_verification_bearer_token(self):
        user = UserFactory(is_verified=False)
        response = self.client.get(
            reverse("user-request-verification-code", kwargs={"pk": user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {user._password_reset_token.encrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid token")

    def test_requesting_verification_code_with_verification_bearer_token(self):
        user = UserFactory(is_verified=False)
        response = self.client.get(
            reverse("user-request-verification-code", kwargs={"pk": user.pk}),
            HTTP_AUTHORIZATION=f"Bearer {user.token.encrypted}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_requesting_temporary_password_without_authentication_credentials(self):
        response = self.client.post(
            reverse("user-request-temporary-password", kwargs={"pk": self.user.pk}),
            data={"email": self.user.email},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(self.user, response.wsgi_request.user)
        self.assertEqual(
            response.wsgi_request.user.token.get_claims(response.data["token"]["encrypted"])["sub"], "password-reset"
        )

    def test_requesting_temporary_password_with_invalid_lookup_field_value(self):
        response = self.client.post(
            reverse("user-request-temporary-password", kwargs={"pk": self.user.pk}),
            data={"email": f"modified.{self.user.email}"},
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_requesting_temporary_password_with_unmatching_lookup_field_value_and_url_kwarg(self):
        user = UserFactory()
        response = self.client.post(
            reverse("user-request-temporary-password", kwargs={"pk": user.pk}),
            data={"email": self.user.email},
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

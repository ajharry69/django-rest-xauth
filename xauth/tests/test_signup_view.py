from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SignUpViewTestCase(APITestCase):
    username, email = 'user', 'user@mail-domain.com'

    def register_user(self, username, email, password):
        return self.client.post(reverse('xauth:signup'), data={
            "username": username,
            "email": email,
            "provider": "EMAIL",  # TODO: Fix must be provided
            "surname": "",
            "first_name": "User",
            "last_name": "One",
            "mobile_number": "",
            "date_of_birth": None,
            "password": password
        })

    def assert_duplicate_unique_property(self, email, password, username, exception_expected: bool = True):
        response = self.register_user(username, email, password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if exception_expected:
            with self.assertRaises(get_user_model().DoesNotExist):
                get_user_model().objects.get(username=username, email=email)

    def assert_signup_success(self, username, email, password):
        response = self.register_user(username, email, password)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # may be None if drf response wrapping was not allowed in settings
        self.assertIsNotNone(response.data.get('payload', None))
        return get_user_model().objects.get_by_natural_key(username=username, )

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email=self.email,
            password='password',
        )

    def test_create_account_with_non_existing_username_and_email_returns_201(self):
        username, email, password = 'user1', 'user1@mail-domain.com', 'user1-password'
        user = self.assert_signup_success(username, email, password)
        self.assertIs(user.check_password(password), True)

    def test_create_account_with_None_password_returns_201_with_unusable_password(self):
        username, email, password = 'user1', 'user1@mail-domain.com', None
        user = self.assert_signup_success(username, email, password)
        self.assertIs(user.has_usable_password(), False)

    def test_create_account_with_empty_password_returns_201_with_unusable_password(self):
        username, email, password = 'user1', 'user1@mail-domain.com', ''
        user = self.assert_signup_success(username, email, password)
        self.assertIs(user.has_usable_password(), False)

    def test_create_account_with_existing_username_returns_400(self):
        username, email, password = self.username, 'user1@mail-domain.com', 'user1-password'
        self.assert_duplicate_unique_property(email, password, username)

    def test_create_account_with_existing_email_returns_400(self):
        username, email, password = 'user1', self.email, 'user1-password'
        self.assert_duplicate_unique_property(email, password, username)

    def test_create_account_with_existing_username_and_email_returns_401(self):
        username, email, password = self.username, self.email, 'user1-password'
        self.assert_duplicate_unique_property(email, password, username, False)

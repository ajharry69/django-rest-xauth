from django.urls import reverse
from rest_framework import status

from xauth.tests import *
from xauth.utils import is_http_response_success


class ProfileViewTestCase(UserAPITestCase):

    def put_user_data(self, removable_keys: list = None):
        """changes last name"""
        if removable_keys is None:
            removable_keys = []
        data = {
            "username": self.user.username,
            "email": self.user.email,
            "provider": self.user.provider,
            "surname": self.user.surname,
            "first_name": self.user.first_name,
            "last_name": self.new_last_name,  # updated
            "mobile_number": self.user.mobile_number,
            "date_of_birth": self.user.date_of_birth,
            'id': self.user.id,
            'is_superuser': self.user.is_superuser,
            'is_staff': self.user.is_staff,
            'is_verified': self.user.is_verified,
            'created_at': self.user.created_at,
        }
        for key in removable_keys:
            data.pop(key)
        return data

    def patch_user_data(self, removable_keys: list = None):
        """changes first name"""
        if removable_keys is None:
            removable_keys = []
        data = {
            "surname": self.user.surname,
            "first_name": self.new_first_name,  # patched
            "last_name": self.user.last_name,
            "mobile_number": self.user.mobile_number,
        }
        for key in removable_keys:
            data.pop(key)
        return data

    def assert_request_methods_status_codes(self, put_patch_code=status.HTTP_200_OK,
                                            delete_code=status.HTTP_204_NO_CONTENT, get_code=status.HTTP_200_OK):
        get_response = self.client.get(reverse('xauth:profile', kwargs={'pk': self.user.id}), )
        # check user password unchanged before tempting an update
        self.assertIs(self.user.check_password(self.password), True)
        # check first name before update
        self.assertEqual(self.user.first_name, self.old_first_name)
        put_response = self.client.put(
            reverse('xauth:profile', kwargs={'pk': self.user.id}),
            data=self.put_user_data(),
        )
        patch_response = self.client.patch(
            reverse('xauth:profile', kwargs={'pk': self.user.id}),
            data=self.patch_user_data(),
        )

        delete_response = self.client.delete(reverse('xauth:profile', kwargs={'pk': self.user.id}), )
        self.assertEqual(get_response.status_code, get_code)
        if put_patch_code:
            self.assertEqual(put_response.status_code, put_patch_code)
            self.assertEqual(patch_response.status_code, put_patch_code)

            if is_http_response_success(put_response.status_code):
                # check user password was unchanged
                self.assertIs(self.user.check_password(self.password), True)
                # check last name was updated
                self.assertEqual(self.get_response_data_with_key(put_response, 'last_name'), self.new_last_name)
                # check first name was update/patched
                self.assertEqual(self.get_response_data_with_key(patch_response, 'first_name'), self.new_first_name)
        if delete_code:
            self.assertEqual(delete_response.status_code, delete_code)

    def test_GET_profile_returns_200_while_PUT_PATCH_OR_DELETE_without_authorization_returns_401(self):
        self.client.credentials()
        self.assert_request_methods_status_codes(
            put_patch_code=status.HTTP_401_UNAUTHORIZED,
            delete_code=status.HTTP_401_UNAUTHORIZED,
        )

    def test_GET_profile_returns_200_while_PUT_PATCH_OR_DELETE_is_not_allowed_to_non_owner_returns_403(self):
        """Non profile owner """
        user_1_encrypted_token = self.user1.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_1_encrypted_token}')
        self.assert_request_methods_status_codes(
            put_patch_code=status.HTTP_403_FORBIDDEN,
            delete_code=status.HTTP_403_FORBIDDEN,
        )

    def test_GET_PUT_PATCH_AND_DELETE_profile_is_allowed_to_owner(self):
        owner_encrypted_token = self.user.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {owner_encrypted_token}')
        self.assert_request_methods_status_codes(
            put_patch_code=status.HTTP_200_OK,
        )

    def test_GET_PUT_PATCH_AND_DELETE_profile_is_allowed_to_superuser(self):
        superuser_encrypted_token = self.superuser.token.encrypted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {superuser_encrypted_token}')
        self.assert_request_methods_status_codes(
            put_patch_code=status.HTTP_200_OK,
        )

    def test_GET_profile_for_existing_account_returns_200(self):
        from requests.auth import _basic_auth_str
        self.client.credentials(HTTP_AUTHORIZATION=_basic_auth_str(self.username, self.password))
        response = self.client.get(reverse('xauth:profile', kwargs={'pk': self.user.id}, ), )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_GET_profile_for_non_existing_account_returns_404(self):
        from requests.auth import _basic_auth_str
        self.client.credentials(HTTP_AUTHORIZATION=_basic_auth_str(self.username, self.password))
        response = self.client.get(reverse('xauth:profile', kwargs={'pk': 123}), )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

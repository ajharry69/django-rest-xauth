from django.test.testcases import TestCase

from xauth.apps.account import admin


class UserCreationFormTestCase(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "user1",
            "email": "user1@domain.com",
            "surname": None,
            "first_name": None,
            "last_name": None,
            "date_of_birth": None,
            "mobile_number": None,
            "password1": "password",
            "password2": "password",
        }
        self.form = admin.UserCreationForm(data=self.data)
        self.form.is_valid()
        self.user = self.form.save()

    def test_save_returns_correct_username_with_correct_password_set(self):
        # updating values
        self.data["first_name"] = "John"
        self.data["last_name"] = "Doe"
        self.data.update(
            {
                "provider": "EMAIL",
                "is_superuser": False,
                "is_staff": False,
                "is_verified": True,
                "is_active": True,
                "password": self.user.password,
            }
        )
        # removing un-necessary keys
        self.data.pop("password1")
        self.data.pop("password2")

        form = admin.UserUpdateForm(data=self.data, instance=self.user)
        valid_form = form.is_valid()
        user = form.save()
        clean_password = form.clean_password()

        self.assertIs(valid_form, True)
        self.assertEqual(clean_password, self.data.get("password", None))
        self.assertEqual(user.username, self.user.username)
        self.assertEqual(user.password, self.user.password)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

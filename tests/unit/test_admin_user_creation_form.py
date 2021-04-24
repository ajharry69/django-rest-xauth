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

    def test_form_is_valid_with_out_all_required_fields_initiated_equals_False(self):
        self.data.pop("password2")
        form = admin.UserCreationForm(data=self.data)
        self.assertIs(form.is_valid(), False)

    def test_form_is_valid_with_all_required_fields_initiated_equals_True(self):
        form = admin.UserCreationForm(data=self.data)
        self.assertIs(form.is_valid(), True)

    def test_form_is_valid_with_un_similar_passwords_equals_False(self):
        self.data["password2"] = f'{self.data.get("password1", "password")}2'
        form = admin.UserCreationForm(data=self.data)
        self.assertIs(form.is_valid(), False)

    def test_clean_password2_raises_ValidationError_if_password1_not_same_as_password2(self):
        self.data["password2"] = f'{self.data.get("password1", "password")}2'
        form = admin.UserCreationForm(data=self.data)
        form.is_valid()
        form.clean_password2()
        self.assertIsNotNone(form.errors)
        self.assertIs(form.has_error("password2", "password_mismatch"), True)

    def test_clean_password2_returns_password2_for_same_password1_and_password2(self):
        self.data["password2"] = self.data.get("password1", "password")
        form = admin.UserCreationForm(data=self.data)
        valid_form = form.is_valid()
        password = form.clean_password2()
        self.assertIs(valid_form, True)
        self.assertEqual(password, self.data.get("password2", None))

    def test_save_returns_correct_username_with_correct_password_set(self):
        self.data["password2"] = self.data.get("password1", "password")
        form = admin.UserCreationForm(data=self.data)
        valid_form = form.is_valid()
        user = form.save()
        self.assertIs(valid_form, True)
        self.assertEqual(user.username, self.data.get("username", None))
        self.assertIs(user.check_password(self.data["password2"]), True)

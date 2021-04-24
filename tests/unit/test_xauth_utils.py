from unittest.case import TestCase

from xauth.utils import get_class


class XauthUtilTest(TestCase):
    def test_class_name_returns_default_class_name_for_empty_class_string(self):
        class_name = get_class("", None)
        self.assertEqual(class_name, None)

    def test_class_name_returns_default_class_name_for_invalid_class_string(self):
        class_name = get_class("invalidclass", XauthUtilTest)
        self.assertEqual(class_name, XauthUtilTest)
        class_name = get_class("xauth.tests.test_xauth_utils.XauthUtil Test", XauthUtilTest)
        self.assertEqual(class_name, XauthUtilTest)

    def test_class_name_returns_correct_class_name_for_valid_class_string(self):
        class_name = get_class(
            "xauth.tests.test_xauth_utils.XauthUtilTest",
        )
        self.assertEqual(class_name, XauthUtilTest)

    def test_class_name_does_not_return_default_class_if_passed_class_name_string_is_valid(self):
        class_name = get_class("xauth.tests.test_xauth_utils.XauthUtilTest", TestCase)
        self.assertNotEqual(class_name, TestCase)

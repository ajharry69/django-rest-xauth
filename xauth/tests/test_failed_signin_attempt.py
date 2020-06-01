from django.test.utils import override_settings

from xauth.tests import *


class FailedSignInAttemptTestCase(UserAPITestCase):
    @override_settings(
        XAUTH={
            'MAXIMUM_SIGN_IN_ATTEMPTS': 5,
        },
    )
    def test_remaining_attempts_with_max_signin_attempts_set_to_5(self):
        attempt_1 = create_failed_signin_attempt(self.user, )
        self.assertEqual(attempt_1.remaining, 4)
        attempt_2 = create_failed_signin_attempt(self.user, count=2)
        self.assertEqual(attempt_2.remaining, 3)

    @override_settings(
        XAUTH={
            'MAXIMUM_SIGN_IN_ATTEMPTS': 0,
        },
    )
    def test_remaining_attempts_with_max_signin_attempts_set_to_0(self):
        attempt_1 = create_failed_signin_attempt(self.user, )
        self.assertEqual(attempt_1.remaining, -1)
        attempt_2 = create_failed_signin_attempt(self.user, count=2)
        self.assertEqual(attempt_2.remaining, -1)

from xauth.tests import *


class MetadataTestCase(APITestCase):
    user = None

    def setUp(self) -> None:
        self.user = create_user('mitch')

    def test_check_temporary_password_returns_true_for_correct_password(self):
        password = 'password'
        meta = update_metadata(self.user, tpass=password)

        self.assertIs(meta.check_temporary_password(raw_password=password), True)
        self.assertIs(meta.check_temporary_password(raw_password='password12'), False)

    def test_check_verification_code_returns_true_for_correct_code(self):
        code = '123456'
        meta = update_metadata(self.user, vcode=code)

        self.assertIs(meta.check_verification_code(raw_code=code), True)
        self.assertIs(meta.check_verification_code(raw_code='654321'), False)

    def test_is_temporary_password_expired_returns_true_for_period_longer_than_30minutes_since_gen_time(self):
        password = 'password'
        tp_gen = timedelta(minutes=-30, seconds=-1)
        meta = update_metadata(self.user, tpass=password, tp_gen=tp_gen)

        self.assertIs(meta.is_temporary_password_expired, True)

    def test_is_verification_code_expired_returns_true_for_period_longer_than_1hour_since_gen_time(self):
        code = '123456'
        vc_gen = timedelta(hours=-1, seconds=-1)
        meta = update_metadata(self.user, vcode=code, vc_gen=vc_gen)

        self.assertIs(meta.is_verification_code_expired, True)

    def test_is_temporary_password_expired_returns_false_for_period_within_30minutes_since_gen_time(self):
        password = 'password'
        tp_gen = timedelta(seconds=1)
        meta = update_metadata(self.user, tpass=password, tp_gen=tp_gen)

        self.assertIs(meta.is_temporary_password_expired, False)

    def test_is_verification_code_expired_returns_false_for_period_within_1hour_since_gen_time(self):
        code = '123456'
        vc_gen = timedelta(seconds=1)
        meta = update_metadata(self.user, vcode=code, vc_gen=vc_gen)

        self.assertIs(meta.is_verification_code_expired, False)
        # string equivalent of a user's metadata object equal to the answer to security question
        self.assertEqual(str(meta), str(meta.security_question.question))

    def test_default_security_question_is_usable_returns_False(self):
        meta = update_metadata(self.user)
        self.assertIs(meta.is_usable_code(meta.security_question_answer), False)

    def test_existing_non_default_security_question_is_usable_returns_True(self):
        security_quest, sec_quest_answer = create_security_question(), 'blue'
        meta = update_metadata(self.user, sec_quest=security_quest, sec_ans=sec_quest_answer, )
        self.assertIs(meta.is_usable_code(meta.security_question_answer), True)
        self.assertIs(meta.check_security_question_answer(sec_quest_answer), True)

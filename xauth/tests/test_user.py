from django.test import override_settings
from django.utils.datetime_safe import datetime

from xauth.models import User
from xauth.tests import *
from xauth.utils import enums
from xauth.utils.settings import DATE_INPUT_FORMAT


class UserTestCase(APITestCase):

    def assert_activation_token_default_expiry(self, token):
        exp_value = token.claims.get('exp', 0)
        default_activation_date_seconds = int(datetime.now().strftime('%s'))
        self.assertGreaterEqual(exp_value, default_activation_date_seconds)
        self.assertEqual(int((exp_value - default_activation_date_seconds) / (60 * 60)), 24)

    def verification_or_reset_succeeded(self, message, token):
        self.assertIsNotNone(token)
        self.assertIsNone(message)
        self.assertEqual(int((token.claims.get('exp', 0) - int(datetime.now().strftime('%s'))) / (60 * 60 * 24)), 60)

    def password_reset_error(self, user, new_password, error_message, correct_password=None, incorrect_password=None):
        if incorrect_password is not None:
            token, message = user.reset_password(
                temporary_password=incorrect_password,
                new_password=new_password,
            )
            self.assertIsNone(token)
            self.assertIsNotNone(message)
            self.assertEqual(message, error_message)
        if correct_password is not None:
            token1, message1 = user.reset_password(
                temporary_password=correct_password,
                new_password=new_password,
            )
            self.assertIsNone(token1)
            self.assertIsNotNone(message1)
            self.assertEqual(message1, error_message)

    def account_verification_error(self, user, error_message, correct_code=None, incorrect_code=None):
        if incorrect_code is not None:
            token, message = user.verify(code=incorrect_code)
            self.assertIsNone(token)
            self.assertIsNotNone(message)
            self.assertEqual(message, error_message)
        if correct_code is not None:
            token1, message1 = user.verify(code=correct_code)
            self.assertIsNone(token1)
            self.assertIsNotNone(message1)
            self.assertEqual(message1, error_message)

    def create_user_with_security_question(self, correct_fav_color):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        user.is_verified = True
        user.is_active = False
        user.save(auto_hash_password=False)
        # updates user's metadata
        meta = update_metadata(user, sec_quest=self.security_quest, sec_ans=correct_fav_color)
        return meta, user

    def setUp(self) -> None:
        self.security_quest = create_security_question()

    def test_get_full_name_returns_username_if_neither_names_are_provided(self):
        """
        Return username if it's provided and neither types of names are provided
        """
        user = User(username='username')
        self.assertEqual(user.get_full_name(), user.username)

    def test_get_full_name_returns_names_in_expected_order(self):
        """
        Expected order {surname} {first-name} {last-name}
        """
        s_name, f_name, l_name = ('Sur', 'First', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_full_name(), f'{s_name} {f_name} {l_name}')

    def test_get_full_name_returns_names_with_first_character_of_every_name_capitalized(self):
        s_name, f_name, l_name = ('Sur', 'first', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_full_name(), f'{s_name} First {l_name}')

    def test_get_full_name_returns_removes_any_spaces_at_the_start_or_end_of_every_name(self):
        s_name, f_name, l_name = ('Sur ', ' first', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_full_name(), f'Sur First {l_name}')

    def test_get_short_name_returns_first_word_in_get_full_name(self):
        s_name, f_name, l_name = ('Sur', 'first', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_short_name(), s_name)

    def test_get_short_name_returns_username_if_no_name_is_provided(self):
        user = User(username='username', )
        self.assertEqual(user.get_short_name(), user.username)

    def test_get_full_name_returns_None_if_neither_names_nor_username_is_provided(self):
        user = User()
        self.assertIsNone(user.get_full_name())

    def test_get_short_name_returns_None_if_neither_names_nor_username_is_provided(self):
        user = User()
        self.assertIsNone(user.get_short_name())

    def test_creating_user_without_username_uses_email_as_username(self):
        email = 'user@mail-domain.com'
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.provider, enums.AuthProvider.EMAIL.name)
        self.assertEqual(user.username, email)
        self.assertIsNotNone(user.password)
        self.assertIs(user.has_usable_password(), False)

    def test_creating_user_with_username_does_not_use_email(self):
        email = 'user@mail-domain.com'
        username = 'user1'
        user = get_user_model().objects.create_user(email=email, username=username)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)

    def test_creating_user_without_manager_methods_works(self):
        """
        Creating user with Django's .create method works same as Managers.create_user
        """
        email = 'user@mail-domain.com'
        user = get_user_model().objects.create(email=email)
        user1 = User(email=f'user.{email}')
        user1.save()
        user2 = User.objects.create(email=f'user1.{email}')
        self.assertEqual(user.username, email)
        self.assertEqual(user.email, email)
        self.assertEqual(user1.username, f'user.{email}')
        self.assertEqual(user2.username, f'user1.{email}')
        self.assertIsNotNone(get_user_model().objects.get_by_natural_key(email))

    def test_check_password_for_created_user_returns_True(self):
        password = 'password123!'
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        user.password = password
        user.save(auto_hash_password=True)
        user1 = User(email='user1@mail-domain.com', password=password)
        user1.save(auto_hash_password=True)

        self.assertEqual(user.check_password(password), True)
        self.assertEqual(user1.check_password(password), True)
        # password hash are never the same even when same password was used
        self.assertNotEqual(user.password, user1.password)

    def test_creating_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None)

    def test_verification_token_expires_after_1_hour_by_default(self):
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        token = user.verification_token
        exp_value = token.claims.get('exp', 0)
        default_activation_date_seconds = int(datetime.now().strftime('%s'))

        self.assertGreaterEqual(exp_value, default_activation_date_seconds)
        self.assertEqual(int((exp_value - default_activation_date_seconds) / (60 * 60)), 1)

    def test_activation_token_expires_after_1_day_by_default(self):
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        token = user.activation_token
        self.assert_activation_token_default_expiry(token)

    def test_activation_token_is_always_returned_for_in_active_users(self):
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        user.is_active = False  # would result to an activation token being returned
        token = user.token
        self.assert_activation_token_default_expiry(token)

    def test_password_reset_token_expires_after_30_minutes_by_default(self):
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        token = user.password_reset_token
        exp_value = token.claims.get('exp', 0)
        default_activation_date_seconds = int(datetime.now().strftime('%s'))

        self.assertGreaterEqual(exp_value, default_activation_date_seconds)
        self.assertEqual(int((exp_value - default_activation_date_seconds) / 60), 30)

    def test_is_verified_for_non_email_provider_or_superuser_and_or_staff_users(self):
        provider = enums.AuthProvider.GOOGLE.name
        phone_provider = enums.AuthProvider.PHONE.name
        user = get_user_model().objects.create(email='user@mail-domain.com', provider=provider)
        user1 = get_user_model().objects.create(email='user1@mail-domain.com', is_superuser=True, password='9V55w0rd')
        user2 = get_user_model().objects.create(email='user2@mail-domain.com', is_staff=True)
        user3 = get_user_model().objects.create(email='user3@mail-domain.com', provider=enums.AuthProvider.EMAIL.name,
                                                is_staff=True)
        user4 = get_user_model().objects.create(email='user4@mail-domain.com', provider=phone_provider, )

        self.assertEqual(user4.provider, phone_provider)
        self.assertIs(user.is_verified, True)
        self.assertIs(user1.is_verified, True)
        self.assertIs(user2.is_verified, True)
        self.assertIs(user3.is_verified, True)
        self.assertIs(user4.is_verified, False)

    def test_creating_user_account_without_password_returns_empty_or_none_password(self):
        password = ''
        password1 = None
        password2 = 'None'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', password=password)
        user1 = get_user_model().objects.create_user(email='user1@mail-domain.com', username='user1234',
                                                     password=password1)
        user2 = get_user_model().objects.create_user(email='user2@mail-domain.com', username='user12345',
                                                     password=password2)
        self.assertIsNotNone(user.password)
        self.assertIsNotNone(user1.password)
        self.assertIs(user2.check_password(raw_password=password2), True)

    def test_request_password_reset_returns_30minute_valid_token_and_temporary_password(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        token, password = user.request_password_reset(send_mail=False)
        metadata = Metadata.objects.get(pk=user.id)

        self.assertIsNotNone(metadata)
        self.assertIsNotNone(token)
        self.assertIsNotNone(password)
        self.assertEqual(int((token.claims.get('exp', 0) - int(datetime.now().strftime('%s'))) / 60), 30)
        self.assertIs(metadata.check_temporary_password(password), True)

    def test_request_verification_returns_1hour_valid_token_and_verification_code(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        token, code = user.request_verification(send_mail=False)
        metadata = Metadata.objects.get(pk=user.id)

        self.assertIsNotNone(metadata)
        self.assertIsNotNone(token)
        self.assertIsNotNone(code)
        self.assertEqual(int((token.claims.get('exp', 0) - int(datetime.now().strftime('%s'))) / (60 * 60)), 1)
        self.assertIs(metadata.check_verification_code(code), True)

    def test_reset_password_with_expired_password_returns_None_token_and_expired_message(self):
        """
        Returned values are same for a correct or incorrect expired reset password
        """
        new_password = 'Qw3ty12345!@#$%'
        incorrect_password = '1ncorrect'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_password = user.request_password_reset(send_mail=False)

        # adjust temporary password's expiry date
        tp_gen_time = timedelta(minutes=-30, seconds=-1)
        update_metadata(user, tp_gen=tp_gen_time)
        self.password_reset_error(user, new_password, 'expired', correct_password, incorrect_password)

    def test_reset_password_with_incorrect_unexpired_password_returns_None_token_and_incorrect_message(self):
        new_password = 'Qw3ty12345!@#$%'
        incorrect_password = '1ncorrect'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_password = user.request_password_reset(send_mail=False)
        self.password_reset_error(user, new_password, 'incorrect', incorrect_password=incorrect_password)

    def test_reset_password_with_correct_password_returns_Token_expiring_after_60days_and_None_message(self):
        new_password = 'Qw3ty12345!@#$%'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        self.assertIs(user.is_verified, False)
        user.is_verified = True
        user.save(auto_hash_password=False, update_fields=['is_active'])
        self.assertIs(user.is_verified, True)
        self.assertIs(user.has_usable_password(), False)
        _, correct_password = user.request_password_reset(send_mail=False)

        token, message = user.reset_password(
            temporary_password=correct_password,
            new_password=new_password,
        )
        # post-reset
        self.verification_or_reset_succeeded(message, token)
        # make sure users password was not changed in the process
        self.assertIs(user.check_password(new_password), True)

    def test_verify_with_expired_code_returns_None_token_and_expired_message(self):
        """
        Returned values are same for a correct or incorrect expired reset password
        """
        incorrect_code = '123456'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_code = user.request_verification(send_mail=False)

        # adjust temporary password's expiry date
        vc_gen_time = timedelta(hours=-1, seconds=-1)
        update_metadata(user, vc_gen=vc_gen_time)
        self.account_verification_error(user, 'expired', correct_code, incorrect_code)

    def test_verify_with_incorrect_unexpired_code_returns_None_token_and_incorrect_message(self):
        incorrect_code = '123456'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_code = user.request_verification(send_mail=False)
        self.account_verification_error(user, 'incorrect', incorrect_code=incorrect_code)

    def test_verify_with_correct_code_returns_Token_expiring_after_60days_and_None_message(self):
        password = 'password'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', password=password)
        _, correct_code = user.request_verification(send_mail=False)

        # pre-verification
        self.assertIs(user.is_verified, False)
        self.assertIs(user.check_password(password), True)
        # verification
        token, message = user.verify(code=correct_code)
        # post-verification
        self.verification_or_reset_succeeded(message, token)
        self.assertIs(user.is_verified, True)
        # make sure users password was not changed in the process
        self.assertIs(user.check_password(password), True)

    def test_request_verification_with_a_verified_user_returns_Token_and_None_code(self):
        password = 'password'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', password=password)
        user.is_verified = True
        user.save(auto_hash_password=False)
        token, code = user.request_verification(send_mail=False)

        self.assertIs(user.is_verified, True)
        self.assertIsNone(code)
        self.assertIsNotNone(token)
        self.assertIs(user.check_password(password), True)

    def test_verifying_a_verified_user_returns_Token_and_None_message(self):
        password = 'password'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', password=password)
        user.is_verified = True
        user.save(auto_hash_password=False)
        token, message = user.verify('123456')

        self.assertIs(user.is_verified, True)
        self.assertIsNone(message)
        self.assertIsNotNone(token)
        self.assertIs(user.check_password(password), True)

    def test_age_with_null_date_of_birth_returns_zero(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', date_of_birth=None)
        user1 = get_user_model().objects.create_user(email='user1@mail-domain.com', date_of_birth='')

        self.assertEqual(user.age(), 0)
        self.assertEqual(user1.age(), 0)

    def test_age_with_non_null_date_of_birth_returns_expected_age_for_valid_age_unit(self):
        dob = (datetime.now() + timedelta(days=-8395)).strftime(DATE_INPUT_FORMAT)
        user = get_user_model().objects.create_user(email='user@mail-domain.com', date_of_birth=dob)
        self.assertEqual(user.age(unit='years'), 23)
        self.assertEqual(user.age(unit='year'), 23)
        self.assertEqual(user.age(unit='y'), 23)
        self.assertEqual(user.age(unit='m'), 279)  # rounded down to the nearest integer value
        self.assertEqual(user.age(unit='w'), 1199)
        self.assertEqual(user.age(unit='d'), 8395)

    def test_age_with_non_null_date_of_birth_returns_expected_age_for_invalid_age_unit(self):
        """returns days duration by default"""
        dob = (datetime.now() + timedelta(days=-8395)).strftime(DATE_INPUT_FORMAT)
        user = get_user_model().objects.create_user(email='user@mail-domain.com', date_of_birth=dob)
        self.assertEqual(user.age(unit='invalid'), 8395)

    def test_activate_account_an_active_user_returns_Token_and_None_message(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        token, message = user.activate_account('does-not-matter')

        self.assertIs(user.is_active, True)
        self.assertIsNone(message)
        self.assertIsNotNone(token)

    def test_creating_superuser_without_password_raises_ValueError(self):
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_superuser(email='user@mail-domain.com', username='user123',
                                                             password=None)

    def test_activate_account_with_incorrect_security_question_answer_returns_Non_None_message(self):
        correct_fav_color = 'blue'
        meta, user = self.create_user_with_security_question(correct_fav_color)
        token, message = user.activate_account('white')

        self.assertIs(user.is_active, False)
        self.assertEqual(message, 'incorrect')
        self.assertIsNone(token)
        self.assertIs(meta.check_security_question_answer(correct_fav_color), True)

    def test_activate_account_with_correct_security_question_answer_returns_Token(self):
        correct_fav_color = 'blue'
        meta, user = self.create_user_with_security_question(correct_fav_color)
        token, message = user.activate_account(correct_fav_color)

        self.assertIs(user.is_active, True)
        self.assertIsNone(message)
        self.assertIsNotNone(token)
        self.assertIs(meta.check_security_question_answer(correct_fav_color), True)

    def test_is_newbie(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', surname='User')

        self.assertEqual(user.is_newbie(), True)
        self.assertEqual(str(user), user.get_full_name())

    def test_get_last_password_change_message(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        user1 = get_user_model().objects.create_user(email='user1@mail-domain.com', )

        cts = [timedelta(days=-365), timedelta(hours=-3), timedelta(minutes=-3), ]
        cts1 = [timedelta(days=-365), timedelta(weeks=-4, days=-3), ]

        create_password_reset_log(user, cts)
        create_password_reset_log(user1, cts1)

        message = user.get_last_password_change_message()
        message1 = user1.get_last_password_change_message()
        self.assertEqual(message, '3 minutes ago')
        self.assertEqual(message1, '1 month ago')

    def test_get_last_password_change_message_with_no_existing_log(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        message = user.get_last_password_change_message()
        self.assertIsNone(message, 'password has never been changed')

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_get_remaining_signin_attempts_with_no_existing_log(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        rem_attempts = user.get_remaining_signin_attempts()
        self.assertEqual(rem_attempts, -1)

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_get_remaining_signin_attempts_with_attempt_count_standing_at_2_returns_3(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        create_failed_signin_attempt(user, 2)
        rem_attempts = user.get_remaining_signin_attempts()
        self.assertEqual(rem_attempts, 3)

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_update_signin_attempts_with_failed_set_to_True_without_existing_logs(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        rem_attempts = user.update_signin_attempts(failed=True)
        self.assertEqual(rem_attempts, 4)

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_update_signin_attempts_with_failed_set_to_True_with_existing_logs(self):
        """total count of existing log is 2"""
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        create_failed_signin_attempt(user, 2)
        rem_attempts = user.update_signin_attempts(failed=True)  # will add one more failed attempt
        self.assertEqual(rem_attempts, 2)

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_update_signin_attempts_with_failed_set_to_False_without_existing_logs(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        rem_attempts = user.update_signin_attempts(failed=False)
        self.assertEqual(rem_attempts, -1)

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_update_signin_attempts_with_failed_set_to_False_with_existing_logs(self):
        """total count of existing log is 2"""
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        create_failed_signin_attempt(user, 2)
        rem_attempts = user.update_signin_attempts(failed=False)  # will add one more failed attempt
        self.assertEqual(rem_attempts, -1)

    @override_settings(XAUTH={'MAXIMUM_SIGN_IN_ATTEMPTS': 5, }, )
    def test_user_account_is_deactivated_upon_sign_in_attempts_exhaustion(self):
        """total count of existing log is 4"""
        email = 'user@mail-domain.com'
        user = get_user_model().objects.create_user(email=email, )
        create_failed_signin_attempt(user, 4)
        # simulates another failed sign-in attempt that'll result in 5 failed attempts upon recording
        rem_attempts = user.update_signin_attempts(failed=True)  # will add one more failed attempt

        user = get_user_model().objects.get_by_natural_key(username=email)
        self.assertIs(user.is_active, False)
        self.assertEqual(rem_attempts, 0)

    def test_add_security_question(self):
        """
        Security question and it's answer is successfully attached to a users account
        """
        user = get_user_model().objects.create_user(email='user@mail-domain.com', )
        questions = add_security_questions()
        question, answer = SecurityQuestion.objects.get(question=questions[0]), "blue"
        added = user.add_security_question(question, answer=answer)

        metadata = Metadata.objects.get(user=user)

        # question was added
        self.assertIs(added, True)
        # question is the same as one present in the database
        self.assertEqual(metadata.security_question_id, question.id)
        # answer to the question in database matches the provided answer
        self.assertIs(metadata.check_security_question_answer(answer), True)

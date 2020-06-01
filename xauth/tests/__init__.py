from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from xauth.models import Metadata, SecurityQuestion, FailedSignInAttempt, PasswordResetLog


def create_user(username):
    return get_user_model().objects.create_user(username=username, email=f'{username}@mail-domain.com')


def update_metadata(user, sec_quest=None, sec_ans=None, tpass=None, vcode=None, tp_gen: timedelta = None,
                    vc_gen: timedelta = None):
    meta, created = Metadata.objects.get_or_create(user=user)
    if sec_quest:
        meta.security_question = sec_quest
    if sec_ans:
        meta.security_question_answer = sec_ans
    meta.temporary_password = tpass
    meta.tp_gen_time = timezone.now() + (tp_gen if tp_gen is not None else timedelta(seconds=0))
    meta.verification_code = vcode
    meta.vc_gen_time = timezone.now() + (vc_gen if vc_gen is not None else timedelta(seconds=0))
    meta.save()

    return meta


def create_security_question(question: str = 'What is your favourite color?', usable: bool = True):
    return SecurityQuestion.objects.create(question=question, usable=usable)


def add_security_questions(questions=None):
    """
    :param questions: list of questions
    :return: list of added question texts
    """
    questions = questions if questions else ["What's your favorite color?", "What's your mothers maiden name?"]
    for q in questions:
        create_security_question(question=q)
    return questions


def get_or_create_security_question(question: str):
    q, c = SecurityQuestion.objects.get_or_create(question=question)
    return q


def create_failed_signin_attempt(user, count: int = 1):
    attempt, created = FailedSignInAttempt.objects.get_or_create(user=user)
    attempt.attempt_count = count
    attempt.save()
    return attempt


def create_password_reset_log(user, change_times: list):
    """
    :param user: for which the log is attached to
    :param change_times: list of `timedelta`s
    """
    for ct in change_times:
        log, created = PasswordResetLog.objects.get_or_create(user=user)
        log.change_time = timezone.now() + ct
        log.save()


class UserAPITestCase(APITestCase):
    @staticmethod
    def get_response_data_with_key(response, data_key: str):
        return response.data.get('payload').get(data_key)

    old_first_name, old_last_name = 'John', 'Doe'
    new_first_name, new_last_name = 'Stephenson', 'Doug'
    username, email, password = 'user', 'user@mail-domain.com', 'password'
    username_1, email_1, password_1 = 'user1', 'user1@mail-domain.com', 'password'
    superuser_username, superuser_email, superuser_password = 'admin', 'admin@mail-domain.com', 'pV55M0r6'

    def setUp(self) -> None:
        self.superuser = get_user_model().objects.create_superuser(
            username=self.superuser_username,
            email=self.superuser_email,
            password=self.superuser_password,
        )
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            first_name=self.old_first_name,
            last_name=self.old_last_name,
        )
        self.user1 = get_user_model().objects.create_user(
            username=self.username_1,
            email=self.email_1,
            password=self.password_1,
        )


class CodeVerificationAPITestCase(UserAPITestCase):

    def code_password_verification(self, response, token):
        from django.utils.datetime_safe import datetime

        user = get_user_model().objects.get_by_natural_key(self.user.username)
        user.is_verified = True
        encrypted_token = self.get_response_data_with_key(response, 'encrypted')
        token_expiry = token.get_claims(encrypted_token, encrypted=True, ).get('exp', 0)
        token_expiry_days = int((token_expiry - int(datetime.now().strftime('%s'))) / (60 * 60 * 24))
        return token_expiry_days, user


class SecurityQuestionAPITestCase(UserAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.security_questions = add_security_questions()
        self.security_question = get_or_create_security_question(self.security_questions[0])

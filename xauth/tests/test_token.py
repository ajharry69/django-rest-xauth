from rest_framework.test import APITestCase

from xauth.utils.token import *


class TokenTest(APITestCase):

    def test_tokens_contains_encrypted_and_normal_keys(self):
        token = Token(payload=1)
        token_keys = [key for key, _ in token.tokens.items()]
        self.assertIn('encrypted', token_keys)
        self.assertIn('normal', token_keys)

    def test_value_of_tokens_same_as_value_generate_token(self):
        token = Token(payload=1)
        _token = token.refresh()
        self.assertEqual(token.tokens, _token)

    def test_value_of_tokens_same_as_values_normal_and_encrypted_properties(self):
        token = Token(payload=1)
        self.assertEqual(token.tokens, {
            'normal': token.normal,
            'encrypted': token.encrypted,
        })

    def test_checked_claims_contains_nbf_exp_and_iat_keys(self):
        token = Token(payload=1)
        checked_claims_keys = [key for key, _ in token.checked_claims.items()]
        self.assertIn('nbf', checked_claims_keys)
        self.assertIn('exp', checked_claims_keys)
        self.assertIn('iat', checked_claims_keys)

    def test_claims_contains_checked_claims(self):
        token = Token(payload=1)
        self.assertDictContainsSubset(token.checked_claims, token.claims)

    def test_claims_contains_payload_key(self):
        token = Token(payload=1)
        claims_keys = [key for key, _ in token.claims.items()]
        self.assertIn(token.payload_key, claims_keys)

    def test_checked_claims_nbf_exp_and_iat_have_alternative_values_if_not_provided(self):
        token = Token(payload=1)
        checked_claims = token.checked_claims
        self.assertIsNot(checked_claims.get('nbf', None), None)
        self.assertIsNot(checked_claims.get('exp', None), None)
        self.assertIsNot(checked_claims.get('iat', None), None)

    def test_claims_payload_is_same_as_constructor_provided(self):
        token = Token(payload=1)
        self.assertEqual(token.claims.get(token.payload_key, None), 1)

    def test_provided_exp_value_greater_than_or_equal_default_activation_date_seconds(self):
        token = Token(payload=1, expiry_period=timedelta(minutes=5))
        exp_value = token.claims.get('exp', 0)
        default_activation_date_seconds = int(datetime.now().strftime('%s'))
        self.assertGreaterEqual(exp_value, default_activation_date_seconds)
        self.assertEqual(int((exp_value - default_activation_date_seconds) / 60), 5)

    def test_provided_activation_date_seconds_matches_nbf_value(self):
        activation_date = datetime.now() + timedelta(minutes=5)
        token = Token(payload=1, activation_date=activation_date)
        self.assertEqual(token.claims.get('nbf', 0), int(activation_date.strftime('%s')))
        self.assertEqual(token.claims.get('exp', 0), int((activation_date + timedelta(days=60)).strftime('%s')))

    def test_checked_claims_throws_assertion_error_if_activation_date_is_greater_than_expiration_date(self):
        activation_date = datetime.now() + timedelta(days=5)
        token = Token(payload=1, activation_date=activation_date, expiry_period=timedelta(seconds=-1))
        with self.assertRaises(AssertionError):
            claims = token.checked_claims
        with self.assertRaisesMessage(AssertionError, 'Expiration date must be a date later than activation date'):
            claims = token.checked_claims

    def test_get_payload_value_without_token_param_same_as_payload(self):
        token = Token(payload=1)
        token.refresh()
        self.assertEqual(token.get_payload(), 1)
        self.assertEqual(token.get_payload(), token.payload)

    def test_get_payload_value_without_token_param_same_as_payload_with_hs256_algorithm(self):
        token = Token(payload=1, signing_algorithm='HS256')
        token.refresh()
        self.assertEqual(token.get_payload(), 1)
        self.assertEqual(token.get_payload(), token.payload)

    def test_accessing_normal_and_encrypted_property_always_returns_tokens_as_opposed_to_their_nullable_counterparts(
            self):
        token = Token(payload=1)
        self.assertIsNone(token._normal)
        self.assertIsNone(token._encrypted)
        self.assertIsNotNone(token.normal)
        self.assertIsNotNone(token.encrypted)
        # `token._normal` or `token._encrypted` are not None after calling `token.normal` or `token.encrypted`
        self.assertIsNotNone(token._normal)
        self.assertIsNotNone(token._encrypted)

    def test_normal_and_encrypted_properties_values_are_always_the_same_as_values_in_tokens(self):
        token = Token(payload=1)
        self.assertEqual(token.tokens.get('normal', None), token.normal)
        self.assertEqual(token.tokens.get('encrypted', None), token.encrypted)

    def test_get_payload(self):
        token = Token(payload=1)
        token1 = Token(payload=111)
        self.assertEqual(token.get_payload(), 1)
        self.assertEqual(token.get_payload(token1.normal, encrypted=False), 111)

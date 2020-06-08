from unittest import TestCase

from xauth import get_next_version


class NextVersionTestCase(TestCase):

    def test_get_next_version(self):
        self.assertEqual(get_next_version('0.0.0'), '0.0.1')
        self.assertEqual(get_next_version('1.0.0'), '1.0.1')
        self.assertEqual(get_next_version('1.0.9'), '1.1.0')
        self.assertEqual(get_next_version('1.9.0'), '1.9.1')
        self.assertEqual(get_next_version('1.9.9'), '2.0.0')
        self.assertEqual(get_next_version('2.0.0'), '2.0.1')
        self.assertEqual(get_next_version('9.9.9'), '10.0.0')
        self.assertEqual(get_next_version('10.9.9'), '11.0.0')

import random
import string

from src import crypt_utils


def _random(length=8):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


class TestCryptUtils:
    def setup_method(self):
        self.main_key = _random()

    def test_random_salt(self):
        auth_key_1, auth_salt_1 = crypt_utils.generate_hash(self.main_key)
        auth_key_2, auth_salt_2 = crypt_utils.generate_hash(self.main_key)
        assert auth_key_1 != auth_key_2
        assert auth_salt_1 != auth_salt_2

    def test_password_hash(self):
        auth_key, auth_salt = crypt_utils.generate_hash(self.main_key)
        assert auth_key != self.main_key
        new_auth_key = crypt_utils.hash_with_salt(self.main_key, auth_salt)
        assert new_auth_key == auth_key

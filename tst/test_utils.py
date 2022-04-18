from src.utils import combine_keys
from src.utils import hash_with_salt
from src.utils import generate_hash
from src.utils import generate_secret_key


class TestUtils:
    def setup_method(self):
        self.main_key = generate_secret_key()
        self.secret_key = generate_secret_key()

    def test_key_generation_random(self):
        assert self.main_key != self.secret_key

    def test_commutative_key_combination(self):
        c1 = combine_keys(self.main_key, self.secret_key)
        c2 = combine_keys(self.main_key, self.secret_key)
        assert c1 == c2

    def test_random_salt(self):
        auth_key_1, auth_salt_1 = generate_hash(self.secret_key, self.main_key)
        auth_key_2, auth_salt_2 = generate_hash(self.secret_key, self.main_key)
        assert auth_key_1 != auth_key_2
        assert auth_salt_1 != auth_salt_2

    def test_password_hash(self):
        auth_key, auth_salt = generate_hash(self.secret_key, self.main_key)
        assert auth_key != self.main_key
        assert auth_key != self.secret_key
        new_auth_key = hash_with_salt(self.secret_key, self.main_key, auth_salt)
        assert new_auth_key == auth_key

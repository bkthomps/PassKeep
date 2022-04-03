import utils


def test_key_generation_random():
    key1 = utils.generate_secret_key()
    key2 = utils.generate_secret_key()
    assert key1 != key2


def test_commutative_key_combination():
    key1 = utils.generate_secret_key()
    key2 = utils.generate_secret_key()
    c1 = utils.combine_keys(key1, key2)
    c2 = utils.combine_keys(key1, key2)
    assert c1 == c2


def test_password_hash():
    master_key = utils.generate_secret_key()
    secret_key = utils.generate_secret_key()
    auth_key, auth_salt = utils.generate_hash(secret_key, master_key)
    assert auth_key != master_key
    assert auth_key != secret_key
    new_auth_key = utils.hash_with_salt(secret_key, master_key, auth_salt)
    assert new_auth_key == auth_key

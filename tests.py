import random
import string
import pytest

import utils

import account


def _random(length=8):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


def _login():
    username = _random()
    password = _random()
    account.signup(username, password, password)
    return account.Account.login(username, password), username, password


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


def test_signup_and_login():
    user_1 = _random()
    pass_1 = _random()
    account.signup(user_1, pass_1, pass_1)
    a = account.Account.login(user_1, pass_1)
    assert a._username == user_1


def test_signup_no_username():
    pass_1 = _random()
    with pytest.raises(account.AccountException):
        account.signup('', pass_1, pass_1)


def test_short_password():
    user_1 = _random()
    with pytest.raises(account.AccountException):
        account.signup(user_1, 'pass_1', 'pass_1')


def test_unequal_passwords():
    user_1 = _random()
    pass_1 = _random()
    with pytest.raises(account.AccountException):
        account.signup(user_1, pass_1, 'pass_1')


def test_account_already_exists():
    user_1 = _random()
    pass_1 = _random()
    account.signup(user_1, pass_1, pass_1)
    with pytest.raises(account.AccountException):
        account.signup(user_1, pass_1, pass_1)


def test_signup_twice():
    user_1 = _random()
    pass_1 = _random()
    user_2 = _random()
    pass_2 = _random()
    account.signup(user_1, pass_1, pass_1)
    account.signup(user_2, pass_2, pass_2)
    a1 = account.Account.login(user_1, pass_1)
    a2 = account.Account.login(user_2, pass_2)
    assert a1._username == user_1
    assert a2._username == user_2


def test_bad_login():
    user_1 = _random()
    pass_1 = _random()
    pass_2 = _random()
    account.signup(user_1, pass_1, pass_1)
    with pytest.raises(account.AccountException):
        account.Account.login(user_1, pass_2)


def test_no_vaults():
    account_1, user_1, pass_1 = _login()
    vaults = account_1.get_vaults()
    assert len(vaults) == 0


def test_get_vaults():
    account_1, user_1, pass_1 = _login()
    n1, d1, p1 = _random(), _random(), _random()
    n2, d2, p2 = _random(), _random(), _random()
    account_1.add_vault(n1, d1, p1)
    account_1.add_vault(n2, d2, p2)
    vaults = account_1.get_vaults()
    assert len(vaults) == 2
    name_1, desc_1, vault_pass_1 = account_1.get_vault(vaults[0][0])
    assert name_1 == n1
    assert desc_1 == d1
    assert vault_pass_1 == p1
    name_2, desc_2, vault_pass_2 = account_1.get_vault(vaults[1][0])
    assert name_2 == n2
    assert desc_2 == d2
    assert vault_pass_2 == p2
    with pytest.raises(account.AccountException):
        account_1.get_vault(0)


def test_get_vault_multi_user():
    a, u, p = _login()
    n1, d1, p1 = _random(), _random(), _random()
    n2, d2, p2 = _random(), _random(), _random()
    a.add_vault(n1, d1, p1)
    vault_1_id = a.get_vaults()[0][0]
    a, u, p = _login()
    a.add_vault(n2, d2, p2)
    vault_2_id = a.get_vaults()[0][0]
    name_2, desc_2, vault_pass_2 = a.get_vault(vault_2_id)
    assert name_2 == n2
    assert desc_2 == d2
    assert vault_pass_2 == p2
    with pytest.raises(account.AccountException):
        a.get_vault(vault_1_id)


def test_get_vault_multi_user_hack():
    a, u1, p = _login()
    n1, d1, p1 = _random(), _random(), _random()
    a.add_vault(n1, d1, p1)
    vault_1_id = a.get_vaults()[0][0]
    a, u2, p = _login()
    a._username = u1
    with pytest.raises(UnicodeDecodeError):
        a.get_vault(vault_1_id)

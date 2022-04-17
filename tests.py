import random
import string
import pytest

import utils

from account import Account
from account import AccountException
from main import _entropy


def _random(length=8):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


def _login():
    username = _random()
    password = _random()
    Account.signup(username, password, password)
    return Account.login(username, password), username, password


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
    main_key = utils.generate_secret_key()
    secret_key = utils.generate_secret_key()
    auth_key, auth_salt = utils.generate_hash(secret_key, main_key)
    assert auth_key != main_key
    assert auth_key != secret_key
    new_auth_key = utils.hash_with_salt(secret_key, main_key, auth_salt)
    assert new_auth_key == auth_key


def test_signup_and_login():
    user_1 = _random()
    pass_1 = _random()
    Account.signup(user_1, pass_1, pass_1)
    a = Account.login(user_1, pass_1)
    assert a._username == user_1


def test_signup_no_username():
    pass_1 = _random()
    with pytest.raises(AccountException):
        Account.signup('', pass_1, pass_1)


def test_short_password():
    user_1 = _random()
    with pytest.raises(AccountException):
        Account.signup(user_1, 'pass_1', 'pass_1')


def test_unequal_passwords():
    user_1 = _random()
    pass_1 = _random()
    with pytest.raises(AccountException):
        Account.signup(user_1, pass_1, 'pass_1')


def test_account_already_exists():
    user_1 = _random()
    pass_1 = _random()
    Account.signup(user_1, pass_1, pass_1)
    with pytest.raises(AccountException):
        Account.signup(user_1, pass_1, pass_1)


def test_signup_twice():
    user_1 = _random()
    pass_1 = _random()
    user_2 = _random()
    pass_2 = _random()
    Account.signup(user_1, pass_1, pass_1)
    Account.signup(user_2, pass_2, pass_2)
    a1 = Account.login(user_1, pass_1)
    a2 = Account.login(user_2, pass_2)
    assert a1._username == user_1
    assert a2._username == user_2


def test_bad_login():
    user_1 = _random()
    pass_1 = _random()
    pass_2 = _random()
    Account.signup(user_1, pass_1, pass_1)
    with pytest.raises(AccountException):
        Account.login(user_1, pass_2)


def test_leaked_password():
    username = _random()
    password = 'password'
    with pytest.raises(AccountException):
        Account.signup(username, password, password)


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
    if vaults[0][0] != n1:
        vaults[0], vaults[1] = vaults[1], vaults[0]
    assert vaults[0][0] == n1
    assert vaults[1][0] == n2
    vault_1 = account_1.get_vault(vaults[0])
    assert vault_1[0] == d1
    assert vault_1[1] == p1
    vault_2 = account_1.get_vault(vaults[1])
    assert vault_2[0] == d2
    assert vault_2[1] == p2


def test_get_vault_multi_user():
    account_1, user_1, pass_1 = _login()
    account_2, user_2, pass_2 = _login()
    n1, d1, p1 = _random(), _random(), _random()
    n2, d2, p2 = _random(), _random(), _random()
    account_1.add_vault(n1, d1, p1)
    account_2.add_vault(n2, d2, p2)
    vaults_1 = account_1.get_vaults()
    vaults_2 = account_2.get_vaults()
    assert len(vaults_1) == 1
    assert len(vaults_2) == 1
    assert vaults_1[0][0] == n1
    assert vaults_2[0][0] == n2
    vault_1 = account_1.get_vault(vaults_1[0])
    assert vault_1[0] == d1
    assert vault_1[1] == p1
    vault_2 = account_1.get_vault(vaults_2[0])
    assert vault_2[0] == d2
    assert vault_2[1] == p2


def test_double_add_vault_repeat_name():
    account_1, user_1, pass_1 = _login()
    n1, d1, p1 = _random(), _random(), _random()
    n2, d2, p2 = _random(), _random(), _random()
    account_1.add_vault(n1, d1, p1)
    with pytest.raises(AccountException):
        account_1.add_vault(n1, d2, p2)
    vaults_1 = account_1.get_vaults()
    assert len(vaults_1) == 1


def test_double_add_vault_different_name():
    account_1, user_1, pass_1 = _login()
    n1, d1, p1 = _random(), _random(), _random()
    n2, d2, p2 = _random(), _random(), _random()
    account_1.add_vault(n1, d1, p1)
    account_1.add_vault(n2, d1, p1)
    vaults_1 = account_1.get_vaults()
    assert len(vaults_1) == 2


def test_entropy_random_passwords():
    assert round(_entropy(''), 1) == 0.0
    assert round(_entropy('[-tyZ'), 1) == 32.0
    assert round(_entropy('m2`?9KzLA,'), 1) == 65.5
    assert round(_entropy('f75^aD<:V[sY4;$'), 1) == 98.3
    assert round(_entropy('"[Ma]|Gx?,tIR2x^3JSA'), 1) == 131.1
    assert round(_entropy('6@g|PtLfs2)/8^vZDOU#]QDB.'), 1) == 163.9
    assert round(_entropy('scn7f19lms'), 1) == 51.7
    assert round(_entropy('WCtlxJrlyu'), 1) == 57.0
    assert round(_entropy('9IvklHqK4Y'), 1) == 59.5
    assert round(_entropy('bhclepcjqs'), 1) == 47.0
    assert round(_entropy('862575'), 1) == 19.9
    assert round(_entropy('5149'), 1) == 13.3


def test_entropy_diceware_passwords():
    assert round(_entropy('lather.busybody'), 1) == 25.8
    assert round(_entropy('wisplike.conflict.follow'), 1) == 38.8
    assert round(_entropy('visible.mobile.aflutter.squint'), 1) == 51.7
    assert round(_entropy('cinema.igloo.concept.porridge.virtual'), 1) == 64.6
    assert round(_entropy('sadly.gotten.bonnet.breezy.mulberry.scorch'), 1) == 77.5
    assert round(_entropy('lather-busybody'), 1) == 25.8

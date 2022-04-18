from dataclasses import dataclass
import random
import string
import pytest

from src.account import Account
from src.account import AccountException


def _random(length=8):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


class TestSignup:
    def setup_method(self):
        self.username = _random()
        self.password = _random()
        self.other_username = _random()
        self.other_password = _random()

    def test_no_username(self):
        with pytest.raises(AccountException):
            Account.signup('', self.password, self.password)

    def test_no_password(self):
        with pytest.raises(AccountException):
            Account.signup(self.username, '', '')

    def test_short_password(self):
        short_password = _random(4)
        with pytest.raises(AccountException):
            Account.signup(self.username, short_password, short_password)

    def test_unequal_passwords(self):
        with pytest.raises(AccountException):
            Account.signup(self.username, self.password, self.other_password)

    def test_account_already_exists(self):
        Account.signup(self.username, self.password, self.password)
        with pytest.raises(AccountException):
            Account.signup(self.username, self.password, self.password)

    def test_signup(self):
        Account.signup(self.username, self.password, self.password)
        account = Account.login(self.username, self.password)
        assert account._username == self.username

    def test_double_signup(self):
        Account.signup(self.username, self.password, self.password)
        Account.signup(self.other_username, self.other_password, self.other_password)
        account = Account.login(self.username, self.password)
        other_account = Account.login(self.other_username, self.other_password)
        assert account._username == self.username
        assert other_account._username == self.other_username

    def test_leaked_password(self):
        password = 'password'
        with pytest.raises(AccountException):
            Account.signup(self.username, password, password)

    def test_bad_login(self):
        Account.signup(self.username, self.password, self.password)
        with pytest.raises(AccountException):
            Account.login(self.username, self.other_password)


class BaseVault:
    @dataclass
    class Vault:
        name: str
        description: str
        password: str

    def setup_method(self):
        self.username = _random()
        self.password = _random()
        Account.signup(self.username, self.password, self.password)
        self.account = Account.login(self.username, self.password)
        self.other_username = _random()
        self.other_password = _random()
        Account.signup(self.other_username, self.other_password, self.other_password)
        self.other_account = Account.login(self.other_username, self.other_password)
        self.vaults = []

    def _add_vault(self, account):
        vault = self.Vault(name=_random(), description=_random(), password=_random())
        self.vaults.append(vault)
        account.add_vault(vault.name, vault.description, vault.password)


class TestVault(BaseVault):
    def setup_method(self):
        super().setup_method()

    def test_no_vaults(self):
        vaults = self.account.get_vaults()
        assert len(vaults) == 0

    def test_get_vaults(self):
        self._add_vault(self.account)
        self._add_vault(self.account)
        vaults = self.account.get_vaults()
        assert len(vaults) == 2
        if vaults[0][0] != self.vaults[0].name:
            vaults[0], vaults[1] = vaults[1], vaults[0]
        assert vaults[0][0] == self.vaults[0].name
        assert vaults[1][0] == self.vaults[1].name
        vault_1 = self.account.get_vault(vaults[0])
        assert vault_1[0] == self.vaults[0].description
        assert vault_1[1] == self.vaults[0].password
        vault_2 = self.account.get_vault(vaults[1])
        assert vault_2[0] == self.vaults[1].description
        assert vault_2[1] == self.vaults[1].password

    def test_get_vault_multi_user(self):
        self._add_vault(self.account)
        self._add_vault(self.other_account)
        vaults_1 = self.account.get_vaults()
        vaults_2 = self.other_account.get_vaults()
        assert len(vaults_1) == 1
        assert len(vaults_2) == 1
        assert vaults_1[0][0] == self.vaults[0].name
        assert vaults_2[0][0] == self.vaults[1].name
        vault_1 = self.account.get_vault(vaults_1[0])
        assert vault_1[0] == self.vaults[0].description
        assert vault_1[1] == self.vaults[0].password
        vault_2 = self.account.get_vault(vaults_2[0])
        assert vault_2[0] == self.vaults[1].description
        assert vault_2[1] == self.vaults[1].password

    def test_double_add_vault_repeat_name(self):
        self._add_vault(self.account)
        with pytest.raises(AccountException):
            self.account.add_vault(self.vaults[0].name, _random(), _random())
        vaults = self.account.get_vaults()
        assert len(vaults) == 1

    def test_double_add_vault_different_name(self):
        self._add_vault(self.account)
        self.account.add_vault(_random(), self.vaults[0].description, self.vaults[0].password)
        vaults = self.account.get_vaults()
        assert len(vaults) == 2

    def test_delete_vault(self):
        self._add_vault(self.account)
        self._add_vault(self.account)
        assert len(self.account.get_vaults()) == 2
        (vault_id, _, _, _, _) = self.account.get_vault_id(self.vaults[0].name)
        self.account.delete_vault(vault_id)
        assert len(self.account.get_vaults()) == 1
        with pytest.raises(AccountException):
            self.account.get_vault_id(self.vaults[0].name)
        (vault_id, _, _, _, _) = self.account.get_vault_id(self.vaults[1].name)
        self.account.delete_vault(vault_id)
        assert len(self.account.get_vaults()) == 0
        with pytest.raises(AccountException):
            self.account.get_vault_id(self.vaults[1].name)


class TestEditVault(BaseVault):
    def setup_method(self):
        super().setup_method()
        self._add_vault(self.account)
        assert len(self.account.get_vaults()) == 1
        vault = self.account.get_vaults()[0]
        vault_name = vault[0]
        (self.vault_id, self.iv, name, description, password) = self.account.get_vault_id(vault_name)
        self.old_vault = self.Vault(name=name, description=description, password=password)
        (description, password) = self.account.get_vault(vault)
        assert vault_name == self.vaults[0].name
        assert description == self.vaults[0].description
        assert password == self.vaults[0].password

    def test_edit_vault_name(self):
        new_name = _random()
        self.account.edit_vault(self.vault_id, self.iv, new_name, self.old_vault.description, self.old_vault.password)
        assert len(self.account.get_vaults()) == 1
        vault = self.account.get_vaults()[0]
        vault_name = vault[0]
        (description, password) = self.account.get_vault(vault)
        assert vault_name == new_name
        assert description == self.old_vault.description
        assert password == self.old_vault.password

    def test_edit_vault_description(self):
        new_description = _random()
        self.account.edit_vault(self.vault_id, self.iv, self.old_vault.name, new_description, self.old_vault.password)
        assert len(self.account.get_vaults()) == 1
        vault = self.account.get_vaults()[0]
        vault_name = vault[0]
        (description, password) = self.account.get_vault(vault)
        assert vault_name == self.old_vault.name
        assert description == new_description
        assert password == self.old_vault.password

    def test_edit_vault_password(self):
        new_password = _random()
        self.account.edit_vault(self.vault_id, self.iv, self.old_vault.name, self.old_vault.description, new_password)
        assert len(self.account.get_vaults()) == 1
        vault = self.account.get_vaults()[0]
        vault_name = vault[0]
        (description, password) = self.account.get_vault(vault)
        assert vault_name == self.old_vault.name
        assert description == self.old_vault.description
        assert password == new_password


class TestUser(BaseVault):
    def setup_method(self):
        super().setup_method()

    def test_delete_user(self):
        with pytest.raises(AccountException):
            Account.signup(self.username, self.password, self.password)
        self.account.delete_user()
        with pytest.raises(AccountException):
            Account.login(self.username, self.password)
        Account.signup(self.username, self.password, self.password)


class TestEditUser(BaseVault):
    def setup_method(self):
        super().setup_method()

    def test_edit_username(self):
        self._add_vault(self.account)
        with pytest.raises(AccountException):
            Account.signup(self.username, self.password, self.password)
        with pytest.raises(AccountException):
            self.account.edit_username(self.username)
        new_username = _random()
        self.account.edit_username(new_username)
        with pytest.raises(AccountException):
            Account.signup(new_username, self.password, self.password)
        Account.login(new_username, self.password)

    def test_edit_password(self):
        self._add_vault(self.account)
        new_password = _random()
        with pytest.raises(AccountException):
            self.account.edit_password(self.password, new_password)
        self.account.edit_password(new_password, new_password)
        with pytest.raises(AccountException):
            Account.login(self.username, self.password)
        Account.login(self.username, new_password)

    def teardown_method(self):
        assert len(self.account.get_vaults()) == 1
        vault = self.account.get_vaults()[0]
        vault_name = vault[0]
        (description, password) = self.account.get_vault(vault)
        assert vault_name == self.vaults[0].name
        assert description == self.vaults[0].description
        assert password == self.vaults[0].password

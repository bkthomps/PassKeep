import random
import string
import pytest

from src import crypt_utils
from src.connection import Connection
from src.vaults import Vaults
from src.vaults import VaultException


def _random(length=8):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


class BaseTestVaults:
    def setup_method(self):
        self.username = _random()
        self.crypt_key = crypt_utils.generate_secret_key()
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)
        assert len(self.vaults.get_vault_names()) == 0
        self.vaults.add_vault('name-1', 'description-1', 'password-1')
        self.vaults.add_vault('name-2', 'description-2', 'password-2')

    def test_with_cache(self):
        pass

    def test_with_db(self):
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)


class TestGetVaultNames(BaseTestVaults):
    def teardown_method(self):
        assert 'name-1' in self.vaults.get_vault_names()
        assert 'name-2' in self.vaults.get_vault_names()


class TestGetVaultData(BaseTestVaults):
    def teardown_method(self):
        (description, password) = self.vaults.get_vault_data('name-1')
        assert description == 'description-1'
        assert password == 'password-1'
        (description, password) = self.vaults.get_vault_data('name-2')
        assert description == 'description-2'
        assert password == 'password-2'


class TestDeleteVault(BaseTestVaults):
    def test_with_cache(self):
        self.vaults.delete_vault('name-1')

    def test_with_db(self):
        self.test_with_cache()
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)

    def teardown_method(self):
        assert 'name-1' not in self.vaults.get_vault_names()
        assert 'name-2' in self.vaults.get_vault_names()


class TestEditVaultName(BaseTestVaults):
    def test_with_cache(self):
        self.vaults.edit_vault_name('name-1', 'new-name-1')

    def test_with_db(self):
        self.test_with_cache()
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)

    def teardown_method(self):
        assert 'name-1' not in self.vaults.get_vault_names()
        assert 'new-name-1' in self.vaults.get_vault_names()
        assert 'name-2' in self.vaults.get_vault_names()
        (description, password) = self.vaults.get_vault_data('new-name-1')
        assert description == 'description-1'
        assert password == 'password-1'
        (description, password) = self.vaults.get_vault_data('name-2')
        assert description == 'description-2'
        assert password == 'password-2'


class TestEditVaultDescription(BaseTestVaults):
    def test_with_cache(self):
        self.vaults.edit_vault_description('name-1', 'new-description-1')

    def test_with_db(self):
        self.test_with_cache()
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)

    def teardown_method(self):
        assert 'name-1' in self.vaults.get_vault_names()
        assert 'name-2' in self.vaults.get_vault_names()
        (description, password) = self.vaults.get_vault_data('name-1')
        assert description == 'new-description-1'
        assert password == 'password-1'
        (description, password) = self.vaults.get_vault_data('name-2')
        assert description == 'description-2'
        assert password == 'password-2'


class TestEditVaultPassword(BaseTestVaults):
    def test_with_cache(self):
        self.vaults.edit_vault_password('name-1', 'new-password-1')

    def test_with_db(self):
        self.test_with_cache()
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)

    def teardown_method(self):
        assert 'name-1' in self.vaults.get_vault_names()
        assert 'name-2' in self.vaults.get_vault_names()
        (description, password) = self.vaults.get_vault_data('name-1')
        assert description == 'description-1'
        assert password == 'new-password-1'
        (description, password) = self.vaults.get_vault_data('name-2')
        assert description == 'description-2'
        assert password == 'password-2'


class TestException:
    def setup_method(self):
        self.username = _random()
        self.crypt_key = crypt_utils.generate_secret_key()
        self.vaults = Vaults(self.username, Connection(), self.crypt_key)
        self.vaults.add_vault('name', 'description', 'password')

    def test_get_vault_data(self):
        with pytest.raises(VaultException):
            self.vaults.get_vault_data('name-1')

    def test_add_vault(self):
        with pytest.raises(VaultException):
            self.vaults.add_vault('name', 'description-1', 'password-1')

    def test_delete_vault(self):
        with pytest.raises(VaultException):
            self.vaults.delete_vault('name-1')

    def test_edit_vault_name(self):
        with pytest.raises(VaultException):
            self.vaults.edit_vault_name('name-1', 'name-1')

    def test_edit_vault_description(self):
        with pytest.raises(VaultException):
            self.vaults.edit_vault_description('name-1', 'description-1')

    def test_edit_vault_password(self):
        with pytest.raises(VaultException):
            self.vaults.edit_vault_password('name-1', 'password-1')

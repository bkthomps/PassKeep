import unicodedata
from datetime import datetime

import keyring

from src import utils
from src.connection import Connection
from src.connection import is_password_leaked
from src.constants import KEYRING_KEY
from src.constants import USERNAME_MAX_LENGTH
from src.constants import PASSWORD_MIN_LENGTH
from src.vaults import Vaults


class AccountException(Exception):
    pass


class Account:
    def __init__(self, username, password):
        if not username or not password:
            raise AccountException('must fill in fields')
        self._username = username
        self._db = Connection()
        statement = 'SELECT auth_key, auth_salt, crypt_salt FROM account WHERE username = ?'
        entries = self._db.query(statement, (self._username,))
        if not entries:
            raise AccountException('username incorrect')
        secret_key = keyring.get_password(KEYRING_KEY, self._username)
        main_key = unicodedata.normalize('NFKD', password)
        if not secret_key:
            raise AccountException('secret key configuration error')
        auth_key = utils.hash_with_salt(secret_key, main_key, entries[1])
        if auth_key != entries[0]:
            raise AccountException('password incorrect')
        crypt_key = utils.hash_with_salt(secret_key, main_key, entries[2])
        self.vaults = Vaults(self._username, self._db, crypt_key)

    @staticmethod
    def _validate_username(username, old_username=None):
        if username == old_username:
            raise AccountException('this username is the same as the current username')
        if not username:
            raise AccountException('username must be filled in')
        if len(username) > USERNAME_MAX_LENGTH:
            raise AccountException('username must be at most 40 characters')

    @staticmethod
    def _validate_password(password, confirm_password, username=None):
        if password != confirm_password:
            raise AccountException('password does not match confirmation')
        if len(password) < PASSWORD_MIN_LENGTH:
            raise AccountException('password must be at least 8 characters')
        if password == username:
            raise AccountException('password must not equal username')
        if is_password_leaked(password):
            raise AccountException('password is present in a public data leak')

    @staticmethod
    def signup(username, password, confirm_password):
        Account._validate_username(username)
        Account._validate_password(password, confirm_password, username)
        connection = Connection()
        entries = connection.query('SELECT username FROM account WHERE username = ?', (username,))
        if entries:
            raise AccountException('username already exists')
        main_key = unicodedata.normalize('NFKD', password)
        secret_key = utils.generate_secret_key()
        auth_key, auth_salt = utils.generate_hash(secret_key, main_key)
        crypt_key, crypt_salt = utils.generate_hash(secret_key, main_key)
        now = datetime.now()
        insert = (username, auth_key, auth_salt, crypt_salt, now, now)
        connection.execute('INSERT INTO account (username, auth_key, auth_salt, crypt_salt, modified, created) '
                           'VALUES (?, ?, ?, ?, ?, ?)', insert)
        keyring.set_password(KEYRING_KEY, username, secret_key)

    def edit_username(self, new_username):
        self._validate_username(new_username, self._username)
        entries = self._db.query('SELECT username, COUNT(username) FROM account WHERE username = ?', (new_username,))
        if entries[1]:
            raise AccountException('username already exists')
        self._db.execute('UPDATE account SET username = ? WHERE username = ?', (new_username, self._username))
        secret_key = keyring.get_password(KEYRING_KEY, self._username)
        keyring.set_password(KEYRING_KEY, new_username, secret_key)
        keyring.delete_password(KEYRING_KEY, self._username)
        self.vaults.update_username(new_username)

    def edit_password(self, password, confirm_password):
        self._validate_password(password, confirm_password)
        main_key = unicodedata.normalize('NFKD', password)
        secret_key = keyring.get_password(KEYRING_KEY, self._username)
        auth_key, auth_salt = utils.generate_hash(secret_key, main_key)
        crypt_key, crypt_salt = utils.generate_hash(secret_key, main_key)
        statement = 'UPDATE account SET auth_key = ?, auth_salt = ?, crypt_salt = ? WHERE username = ?'
        self._db.execute(statement, (auth_key, auth_salt, crypt_salt, self._username))
        self.vaults.update_vaults_crypt(crypt_key)

    def delete_user(self):
        self._db.execute('DELETE FROM account WHERE username = ?', (self._username,))
        keyring.delete_password(KEYRING_KEY, self._username)

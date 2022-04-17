import unicodedata
import utils
from datetime import datetime

import keyring
from Crypto.Cipher import AES

from connection import Connection
from connection import is_password_leaked

KEYRING_KEY = 'bkthomps-passkeep'


class AccountException(Exception):
    pass


class Account:
    def __init__(self, username):
        self._username = username
        self._crypt_key = None
        self._db = Connection(username)

    @staticmethod
    def signup(username, password, confirm_password):
        if len(username) == 0:
            raise AccountException('username must be filled in')
        if len(username) > 40:
            raise AccountException('username must be at most 40 characters')
        if password != confirm_password:
            raise AccountException('password does not match confirmation')
        if len(password) < 8:
            raise AccountException('password must be at least 8 characters')
        if password == username:
            raise AccountException('password must not equal username')
        if is_password_leaked(password):
            raise AccountException('password is present in a public data leak')
        connection = Connection(username)
        entries = connection.query('SELECT username, COUNT(username) FROM account WHERE username = ?', (username,))
        if entries[1]:
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

    @staticmethod
    def login(username, password):
        if len(username) == 0 or len(password) == 0:
            raise AccountException('must fill in fields')
        account = Account(username)
        secret_key = keyring.get_password(KEYRING_KEY, username)
        main_key = unicodedata.normalize('NFKD', password)
        if not secret_key or not account._valid_user(secret_key, main_key):
            raise AccountException('username or password incorrect')
        return account

    def _valid_user(self, secret_key, password):
        main_key = unicodedata.normalize('NFKD', password)
        statement = 'SELECT username, auth_key, auth_salt, crypt_salt, COUNT(*) FROM account WHERE username = ?'
        entries = self._db.query(statement, (self._username,))
        if entries[4] == 0:
            return False
        auth_key = utils.hash_with_salt(secret_key, main_key, entries[2])
        if auth_key != entries[1]:
            return False
        self._crypt_key = utils.hash_with_salt(secret_key, main_key, entries[3])
        return True

    def add_vault(self, vault_name, description, password):
        if self._does_vault_exist(vault_name):
            raise AccountException('vault name already exists for this user')
        crypt_bytes = utils.byte_string(self._crypt_key)
        vault_name_bytes = utils.zero_pad(vault_name).encode()
        description_bytes = utils.zero_pad(description).encode()
        password_bytes = utils.zero_pad(password).encode()
        cipher = AES.new(crypt_bytes, AES.MODE_CBC)
        iv = cipher.IV
        encrypted_vault_name = utils.base64_string(cipher.encrypt(vault_name_bytes))
        encrypted_description = utils.base64_string(cipher.encrypt(description_bytes))
        encrypted_password = utils.base64_string(cipher.encrypt(password_bytes))
        now = datetime.now()
        insert = (iv, self._username, encrypted_vault_name, encrypted_description, encrypted_password, now, now)
        self._db.execute('INSERT INTO vault (iv, username, vault_name, description, password, modified, created) '
                         'VALUES (?, ?, ?, ?, ?, ?, ?)', insert)

    def _does_vault_exist(self, vault_name):
        vaults = self.get_vaults()
        for vault in vaults:
            if vault[0] == vault_name:
                return True
        return False

    def get_vaults(self):
        crypt_bytes = utils.byte_string(self._crypt_key)
        statement = 'SELECT iv, vault_name, description, password FROM vault WHERE username = ?'
        rows = self._db.query_all(statement, (self._username,))
        vaults = []
        for row in rows:
            cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=row[0])
            vault_name = utils.byte_to_str(cipher.decrypt(utils.byte_string(row[1])))
            vaults.append((vault_name, cipher, row[2], row[3]))
        return vaults

    @staticmethod
    def get_vault(vault_data):
        cipher = vault_data[1]
        description = utils.byte_to_str(cipher.decrypt(utils.byte_string(vault_data[2])))
        password = utils.byte_to_str(cipher.decrypt(utils.byte_string(vault_data[3])))
        return description, password

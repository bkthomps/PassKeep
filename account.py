import unicodedata
from datetime import datetime

import keyring
from Crypto.Cipher import AES

from connection import Connection
import utils


class AccountException(Exception):
    pass


def signup(username, password, confirm_password):
    if len(username) == 0:
        raise AccountException("Username must be filled in")
    if len(username) > 40:
        raise AccountException("Username must be at most 40 characters")
    if password != confirm_password:
        raise AccountException("Password does not match confirmation")
    if len(password) < 8:
        raise AccountException("Password must be at least 8 characters")
    if password == username:
        raise AccountException("Password must not equal username")
    connection = Connection(username)
    entries = connection.query("SELECT username, COUNT(username) FROM account WHERE username = ?", (username,))
    if entries[1]:
        raise AccountException("Username already exists")
    master_key = unicodedata.normalize('NFKD', password)
    secret_key = utils.generate_secret_key()
    auth_key, auth_salt = utils.generate_hash(secret_key, master_key)
    crypt_key, crypt_salt = utils.generate_hash(secret_key, master_key)
    now = datetime.now()
    insert = (username, auth_key, auth_salt, crypt_salt, now, now)
    connection.execute("INSERT INTO account (username, auth_key, auth_salt, crypt_salt, modified, created) "
                       "VALUES (?, ?, ?, ?, ?, ?)", insert)
    keyring.set_password("bkthomps-passkeep", username, secret_key)


class Account:
    def __init__(self, username):
        self._username = username
        self._crypt_key = None
        self._db = Connection(username)

    @staticmethod
    def login(username, password):
        if len(username) == 0 or len(password) == 0:
            raise AccountException("Must fill in fields")
        account = Account(username)
        secret_key = keyring.get_password("bkthomps-passkeep", username)
        master_key = unicodedata.normalize('NFKD', password)
        if not secret_key or not account._valid_user(secret_key, master_key):
            raise AccountException("Username or password incorrect")
        return account

    def _valid_user(self, secret_key, password):
        master_key = unicodedata.normalize('NFKD', password)
        statement = "SELECT username, auth_key, auth_salt, crypt_salt, COUNT(*) FROM account WHERE username = ?"
        entries = self._db.query(statement, (self._username,))
        if entries[4] == 0:
            return False
        auth_key = utils.hash_with_salt(secret_key, master_key, entries[2])
        if auth_key != entries[1]:
            return False
        self._crypt_key = utils.hash_with_salt(secret_key, master_key, entries[3])
        return True

    def add_vault(self, account_name, description, password):
        crypt_bytes = utils.byte_string(self._crypt_key)
        account_name_bytes = utils.zero_pad(account_name).encode()
        description_bytes = utils.zero_pad(description).encode()
        password_bytes = utils.zero_pad(password).encode()
        cipher = AES.new(crypt_bytes, AES.MODE_CBC)
        iv = cipher.IV
        encrypted_account_name = utils.base64_string(cipher.encrypt(account_name_bytes))
        encrypted_description = utils.base64_string(cipher.encrypt(description_bytes))
        encrypted_password = utils.base64_string(cipher.encrypt(password_bytes))
        now = datetime.now()
        insert = (iv, self._username, encrypted_account_name, encrypted_description, encrypted_password, now, now)
        self._db.execute("INSERT INTO vault (iv, username, account_name, description, password, modified, created) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?)", insert)

    def get_vaults(self):
        crypt_bytes = utils.byte_string(self._crypt_key)
        statement = "SELECT id, iv, account_name FROM vault WHERE username = ?"
        rows = self._db.query_all(statement, (self._username,))
        vaults = []
        for row in rows:
            vault_id = row[0]
            cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=row[1])
            account_name = utils.byte_to_str(cipher.decrypt(utils.byte_string(row[2])))
            vaults.append((vault_id, account_name))
        return vaults

    def get_vault(self, vault_id):
        crypt_bytes = utils.byte_string(self._crypt_key)
        statement = "SELECT username, iv, account_name, description, password FROM vault WHERE id = ?"
        entries = self._db.query(statement, (vault_id,))
        if not entries or entries[0] != self._username:
            raise AccountException("Invalid vault id")
        cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=entries[1])
        account_name = cipher.decrypt(utils.byte_string(entries[2])).decode().rstrip('\x00')
        description = cipher.decrypt(utils.byte_string(entries[3])).decode().rstrip('\x00')
        password = cipher.decrypt(utils.byte_string(entries[4])).decode().rstrip('\x00')
        return account_name, description, password

import base64
import secrets
import sqlite3
import unicodedata
from datetime import datetime

import keyring
from Crypto.Cipher import AES
from passlib.hash import pbkdf2_sha256


class Account:
    def __init__(self, username):
        self._username = username
        self._crypt_key = None
        self._db = sqlite3.connect('passkeep.db')

    def _query(self, statement, arguments):
        c = self._db.cursor()
        c.execute(statement, arguments)
        entries = c.fetchone()
        c.close()
        return entries

    def _query_all(self, statement, arguments):
        c = self._db.cursor()
        c.execute(statement, arguments)
        entries = c.fetchall()
        c.close()
        return entries

    def _execute(self, statement, arguments):
        c = self._db.cursor()
        c.execute(statement, arguments)
        self._db.commit()
        c.close()

    @classmethod
    def _combine_keys(cls, secret_key, master_key):
        secret_key_bytes = cls._byte_string(secret_key)
        master_key_bytes = cls._byte_string(master_key)
        combined_key_bytes = bytearray(32)
        for i in range(32):
            combined_key_bytes[i] = secret_key_bytes[i] ^ master_key_bytes[i]
        return cls._base64_string(combined_key_bytes)

    @staticmethod
    def _byte_string(base64_string):
        return base64.b64decode(base64_string + "===", b'./')

    @staticmethod
    def _base64_string(byte_string):
        return base64.b64encode(byte_string, b'./').decode('utf-8').replace("=", "")

    def signup(self, password, confirmPassword):
        if len(self._username) == 0:
            raise Exception("Username must be filled in")
        if len(self._username) > 40:
            raise Exception("Username must be at most 40 characters")
        if password != confirmPassword:
            raise Exception("Password does not match confirmation")
        if len(password) < 8:
            raise Exception("Password must be at least 8 characters")
        if password == self._username:
            raise Exception("Password must not equal username")
        entries = self._query("SELECT username, COUNT(username) FROM account WHERE username = ?", (self._username,))
        if entries[1] > 0:
            raise Exception("Username already exists")
        self._create_account(password)

    def _create_account(self, password):
        master_key = unicodedata.normalize('NFKD', password)
        secret_key = self._generate_secret_key()
        auth_key, auth_salt = self._generate_hash(secret_key, master_key)
        crypt_key, crypt_salt = self._generate_hash(secret_key, master_key)
        now = datetime.now()
        insert = (self._username, auth_key, auth_salt, crypt_salt, now, now)
        self._execute("INSERT INTO account (username, auth_key, auth_salt, crypt_salt, modified, created) "
                      "VALUES (?, ?, ?, ?, ?, ?)", insert)
        keyring.set_password("bkthomps-passkeep", self._username, secret_key)
        self._crypt_key = crypt_key

    @classmethod
    def _generate_secret_key(cls):
        secret_key_bytes = secrets.token_bytes(32)
        return cls._base64_string(secret_key_bytes)

    @classmethod
    def _generate_hash(cls, secret_key, master_key):
        pair = pbkdf2_sha256.using(rounds=250_000, salt_size=32).hash(master_key)
        salt = pair.split("$")[3]
        hashed = pair.split("$")[4]
        key = cls._combine_keys(secret_key, hashed)
        return key, salt

    def login(self, password):
        if len(self._username) == 0 or len(password) == 0:
            raise Exception("Must fill in fields")
        secret_key = keyring.get_password("bkthomps-passkeep", self._username)
        master_key = unicodedata.normalize('NFKD', password)
        if not secret_key or not self._valid_user(secret_key, master_key):
            raise Exception("Username or password incorrect")

    def _valid_user(self, secret_key, password):
        master_key = unicodedata.normalize('NFKD', password)
        statement = "SELECT username, auth_key, auth_salt, crypt_salt, COUNT(*) FROM account WHERE username = ?"
        entries = self._query(statement, (self._username,))
        if entries[4] == 0:
            return False
        auth_key = self._hash_with_salt(secret_key, master_key, entries[2])
        if auth_key != entries[1]:
            return False
        self._crypt_key = self._hash_with_salt(secret_key, master_key, entries[3])
        return True

    @classmethod
    def _hash_with_salt(cls, secret_key, master_key, salt):
        salt_bytes = cls._byte_string(salt)
        pair = pbkdf2_sha256.using(rounds=250_000, salt=salt_bytes).hash(master_key)
        return cls._combine_keys(secret_key, pair.split("$")[4])

    def add_vault(self, account_name, description, password):
        crypt_bytes = self._byte_string(self._crypt_key)
        account_name_bytes = self._zero_pad(account_name).encode()
        description_bytes = self._zero_pad(description).encode()
        password_bytes = self._zero_pad(password).encode()
        cipher = AES.new(crypt_bytes, AES.MODE_CBC)
        iv = cipher.IV
        encrypted_account_name = self._base64_string(cipher.encrypt(account_name_bytes))
        encrypted_description = self._base64_string(cipher.encrypt(description_bytes))
        encrypted_password = self._base64_string(cipher.encrypt(password_bytes))
        now = datetime.now()
        insert = (iv, self._username, encrypted_account_name, encrypted_description, encrypted_password, now, now)
        self._execute("INSERT INTO vault (iv, username, account_name, description, password, modified, created) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?)", insert)

    @staticmethod
    def _zero_pad(string):
        return string.ljust(len(string) + 16 - len(string) % 16, '\0')

    @staticmethod
    def _byte_to_str(byte):
        return str(byte)[2:][:-1].split("\\x00", 1)[0]

    def get_vaults(self):
        crypt_bytes = self._byte_string(self._crypt_key)
        statement = "SELECT id, iv, account_name FROM vault WHERE username = ?"
        rows = self._query_all(statement, (self._username,))
        vaults = []
        for row in rows:
            vault_id = row[0]
            cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=row[1])
            account_name = self._byte_to_str(cipher.decrypt(self._byte_string(row[2])))
            vaults.append((vault_id, account_name))
        return vaults

    def get_vault(self, vault_id):
        crypt_bytes = self._byte_string(self._crypt_key)
        statement = "SELECT iv, account_name, description, password FROM vault WHERE id = ?"
        entries = self._query(statement, (vault_id,))
        cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=entries[0])
        account_name = cipher.decrypt(self._byte_string(entries[1])).decode()
        description = cipher.decrypt(self._byte_string(entries[2])).decode()
        password = cipher.decrypt(self._byte_string(entries[3])).decode()
        return account_name, description, password

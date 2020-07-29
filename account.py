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
        self.__username = username
        self.__crypt_key = None
        self.__db = sqlite3.connect('passkeep.db')

    def __query(self, statement, arguments):
        c = self.__db.cursor()
        c.execute(statement, arguments)
        entries = c.fetchone()
        c.close()
        return entries

    def __query_all(self, statement, arguments):
        c = self.__db.cursor()
        c.execute(statement, arguments)
        entries = c.fetchall()
        c.close()
        return entries

    def __execute(self, statement, arguments):
        c = self.__db.cursor()
        c.execute(statement, arguments)
        self.__db.commit()
        c.close()

    @classmethod
    def __combine_keys(cls, secret_key, master_key):
        secret_key_bytes = cls.__byte_string(secret_key)
        master_key_bytes = cls.__byte_string(master_key)
        combined_key_bytes = bytearray(32)
        for i in range(32):
            combined_key_bytes[i] = secret_key_bytes[i] ^ master_key_bytes[i]
        return cls.__base64_string(combined_key_bytes)

    @staticmethod
    def __byte_string(base64_string):
        return base64.b64decode(base64_string + "===", "./")

    @staticmethod
    def __base64_string(byte_string):
        return base64.b64encode(byte_string, b'./').decode('utf-8').replace("=", "")

    def signup(self, password, confirmPassword):
        if len(self.__username) == 0:
            raise Exception("Username must be filled in")
        if len(self.__username) > 40:
            raise Exception("Username must be at most 40 characters")
        if password != confirmPassword:
            raise Exception("Password does not match confirmation")
        if len(password) < 8:
            raise Exception("Password must be at least 8 characters")
        if password == self.__username:
            raise Exception("Password must not equal username")
        entries = self.__query("SELECT username, COUNT(username) FROM account WHERE username = ?", (self.__username,))
        if entries[1] > 0:
            raise Exception("Username already exists")
        self.__create_account(password)

    def __create_account(self, password):
        master_key = unicodedata.normalize('NFKD', password)
        secret_key = self.__generate_secret_key()
        auth_key, auth_salt = self.__generate_hash(secret_key, master_key)
        crypt_key, crypt_salt = self.__generate_hash(secret_key, master_key)
        now = datetime.now()
        insert = (self.__username, auth_key, auth_salt, crypt_salt, now, now)
        self.__execute("INSERT INTO account (username, auth_key, auth_salt, crypt_salt, modified, created) "
                       "VALUES (?, ?, ?, ?, ?, ?)", insert)
        keyring.set_password("bkthomps-passkeep", self.__username, secret_key)
        self.__crypt_key = crypt_key

    @classmethod
    def __generate_secret_key(cls):
        secret_key_bytes = secrets.token_bytes(32)
        return cls.__base64_string(secret_key_bytes)

    @classmethod
    def __generate_hash(cls, secret_key, master_key):
        pair = pbkdf2_sha256.using(rounds=250_000, salt_size=32).hash(master_key)
        salt = pair.split("$")[3]
        hashed = pair.split("$")[4]
        key = cls.__combine_keys(secret_key, hashed)
        return key, salt

    def login(self, password):
        if len(self.__username) == 0 or len(password) == 0:
            raise Exception("Must fill in fields")
        secret_key = keyring.get_password("bkthomps-passkeep", self.__username)
        master_key = unicodedata.normalize('NFKD', password)
        if not secret_key or not self.__valid_user(secret_key, master_key):
            raise Exception("Username or password incorrect")

    def __valid_user(self, secret_key, password):
        master_key = unicodedata.normalize('NFKD', password)
        statement = "SELECT username, auth_key, auth_salt, crypt_salt, COUNT(*) FROM account WHERE username = ?"
        entries = self.__query(statement, (self.__username,))
        if entries[4] == 0:
            return False
        auth_key = self.__hash_with_salt(secret_key, master_key, entries[2])
        if auth_key != entries[1]:
            return False
        self.__crypt_key = self.__hash_with_salt(secret_key, master_key, entries[3])
        return True

    @classmethod
    def __hash_with_salt(cls, secret_key, master_key, salt):
        salt_bytes = cls.__byte_string(salt)
        pair = pbkdf2_sha256.using(rounds=250_000, salt=salt_bytes).hash(master_key)
        return cls.__combine_keys(secret_key, pair.split("$")[4])

    def add_vault(self, account_name, description, password):
        crypt_bytes = self.__byte_string(self.__crypt_key)
        account_name_bytes = self.__zero_pad(account_name).encode()
        description_bytes = self.__zero_pad(description).encode()
        password_bytes = self.__zero_pad(password).encode()
        cipher = AES.new(crypt_bytes, AES.MODE_CBC)
        iv = cipher.IV
        encrypted_account_name = self.__base64_string(cipher.encrypt(account_name_bytes))
        encrypted_description = self.__base64_string(cipher.encrypt(description_bytes))
        encrypted_password = self.__base64_string(cipher.encrypt(password_bytes))
        now = datetime.now()
        insert = (iv, self.__username, encrypted_account_name, encrypted_description, encrypted_password, now, now)
        self.__execute("INSERT INTO vault (iv, username, account_name, description, password, modified, created) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)", insert)

    @staticmethod
    def __zero_pad(string):
        return string.ljust(len(string) + 16 - len(string) % 16, '\0')

    def get_vaults(self):
        crypt_bytes = self.__byte_string(self.__crypt_key)
        statement = "SELECT id, iv, account_name FROM vault WHERE username = ?"
        rows = self.__query_all(statement, (self.__username,))
        vaults = []
        for row in rows:
            vault_id = row[0]
            cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=row[1])
            account_name = cipher.decrypt(self.__byte_string(row[2])).decode()
            vaults.append((vault_id, account_name))
        return vaults

    def get_vault(self, vault_id):
        crypt_bytes = self.__byte_string(self.__crypt_key)
        statement = "SELECT iv, account_name, description, password FROM vault WHERE id = ?"
        entries = self.__query(statement, (vault_id,))
        cipher = AES.new(crypt_bytes, AES.MODE_CBC, iv=entries[0])
        account_name = cipher.decrypt(self.__byte_string(entries[1])).decode()
        description = cipher.decrypt(self.__byte_string(entries[2])).decode()
        password = cipher.decrypt(self.__byte_string(entries[3])).decode()
        return account_name, description, password

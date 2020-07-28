import base64
import secrets
import sqlite3
import unicodedata
from datetime import datetime

import keyring
from passlib.hash import pbkdf2_sha256


class Account:
    def __init__(self, username):
        self.__username = username
        self.__crypt_key = None
        self.__db = sqlite3.connect('passkeep.db')

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
        c = self.__db.cursor()
        c.execute("SELECT username, COUNT(username) FROM account WHERE username = ?", (self.__username,))
        entries = c.fetchone()
        c.close()
        if entries[1] > 0:
            raise Exception("Username already exists")
        self.__create_account(password)

    def __create_account(self, password):
        master_key = unicodedata.normalize('NFKD', password)
        # Values used for authentication (logging in)
        auth = pbkdf2_sha256.using(rounds=250_000, salt_size=32).hash(master_key)
        auth_salt = auth.split("$")[3]
        auth_hashed = auth.split("$")[4]
        # Values used for encryption (encrypting the vault keys)
        crypt = pbkdf2_sha256.using(rounds=250_000, salt_size=32).hash(master_key)
        crypt_salt = crypt.split("$")[3]
        crypt_hashed = crypt.split("$")[4]
        # Create a secret key
        secret_key_bytes = secrets.token_bytes(32)
        secret_key = base64.b64encode(secret_key_bytes, b'./').decode('utf-8').replace("=", "")
        # Key used for authentication
        auth_bytes = base64.b64decode(auth_hashed + "===", "./")
        auth_xor = bytearray(32)
        for i in range(32):
            auth_xor[i] = secret_key_bytes[i] ^ auth_bytes[i]
        auth_key = base64.b64encode(auth_xor, b'./').decode('utf-8').replace("=", "")
        # Key used for encryption
        crypt_bytes = base64.b64decode(crypt_hashed + "===", "./")
        crypt_xor = bytearray(32)
        for i in range(32):
            crypt_xor[i] = secret_key_bytes[i] ^ crypt_bytes[i]
        crypt_key = base64.b64encode(crypt_xor, b'./').decode('utf-8').replace("=", "")
        c = self.__db.cursor()
        now = datetime.now()
        insert = (self.__username, auth_key, auth_salt, crypt_salt, now, now)
        c.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?)", insert)
        self.__db.commit()
        c.close()
        keyring.set_password("bkthomps-passkeep", self.__username, secret_key)

    def login(self, password):
        if len(self.__username) == 0 or len(password) == 0:
            raise Exception("Must fill in fields")
        secret_key = keyring.get_password("bkthomps-passkeep", self.__username)
        master_key = unicodedata.normalize('NFKD', password)
        if not secret_key or not self.__valid_user(secret_key, master_key):
            raise Exception("Username or password incorrect")

    def __valid_user(self, secret_key, password):
        c = self.__db.cursor()
        c.execute("SELECT username, COUNT(username) FROM account WHERE username = ?", (self.__username,))
        entries = c.fetchone()
        if entries[1] == 0:
            return False
        c.execute("SELECT auth_key, auth_salt, crypt_salt FROM account WHERE username = ?", (self.__username,))
        entries = c.fetchone()
        c.close()
        auth_key = entries[0]
        auth_salt = entries[1]
        auth_salt_bytes = base64.b64decode(auth_salt + "===", "./")
        auth = pbkdf2_sha256.using(rounds=250_000, salt=auth_salt_bytes).hash(password)
        auth_hashed = auth.split("$")[4]
        secret_key_bytes = base64.b64decode(secret_key + "===", "./")
        auth_bytes = base64.b64decode(auth_hashed + "===", "./")
        auth_xor = bytearray(32)
        for i in range(32):
            auth_xor[i] = secret_key_bytes[i] ^ auth_bytes[i]
        auth_key_compare = base64.b64encode(auth_xor, b'./').decode('utf-8').replace("=", "")
        return auth_key == auth_key_compare

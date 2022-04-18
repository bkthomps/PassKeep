import base64
import secrets

from passlib.hash import pbkdf2_sha256

from src.constants import HASH_ROUNDS
from src.constants import SALT_SIZE


def byte_string(_base64_string):
    return base64.b64decode(_base64_string + '===', b'./')


def base64_string(_byte_string):
    return base64.b64encode(_byte_string, b'./').decode('utf-8').replace('=', '')


def generate_secret_key():
    secret_key_bytes = secrets.token_bytes(SALT_SIZE)
    return base64_string(secret_key_bytes)


def generate_hash(secret_key, main_key):
    pair = pbkdf2_sha256.using(rounds=HASH_ROUNDS, salt_size=SALT_SIZE).hash(main_key)
    salt = pair.split('$')[3]
    hashed = pair.split('$')[4]
    key = combine_keys(secret_key, hashed)
    return key, salt


def combine_keys(secret_key, main_key):
    secret_key_bytes = byte_string(secret_key)
    main_key_bytes = byte_string(main_key)
    combined_key_bytes = bytearray(SALT_SIZE)
    for i in range(SALT_SIZE):
        combined_key_bytes[i] = secret_key_bytes[i] ^ main_key_bytes[i]
    return base64_string(combined_key_bytes)


def hash_with_salt(secret_key, main_key, salt):
    salt_bytes = byte_string(salt)
    pair = pbkdf2_sha256.using(rounds=HASH_ROUNDS, salt=salt_bytes).hash(main_key)
    return combine_keys(secret_key, pair.split('$')[4])


def zero_pad(string):
    return string.ljust(len(string) + SALT_SIZE // 2 - len(string) % (SALT_SIZE // 2), '\0')


def byte_to_str(byte):
    return str(byte)[2:][:-1].split('\\x00', 1)[0]

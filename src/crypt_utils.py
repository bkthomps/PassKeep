import base64

from passlib.hash import pbkdf2_sha256

from src import constants


def byte_string(_base64_string):
    return base64.b64decode(_base64_string + '===', b'./')


def base64_string(_byte_string):
    return base64.b64encode(_byte_string, b'./').decode('utf-8').replace('=', '')


def generate_hash(main_key):
    pair = pbkdf2_sha256.using(rounds=constants.HASH_ROUNDS, salt_size=constants.SALT_SIZE).hash(main_key)
    salt = pair.split('$')[3]
    hashed = pair.split('$')[4]
    return hashed, salt


def hash_with_salt(main_key, salt):
    salt_bytes = byte_string(salt)
    pair = pbkdf2_sha256.using(rounds=constants.HASH_ROUNDS, salt=salt_bytes).hash(main_key)
    return pair.split('$')[4]


def zero_pad(string):
    half_salt_size = constants.SALT_SIZE // 2
    return string.ljust(len(string) + half_salt_size - len(string) % half_salt_size, '\0')


def byte_to_str(byte):
    return str(byte)[2:][:-1].split('\\x00', 1)[0]


def encrypt(cipher, plaintext):
    plaintext_bytes = zero_pad(plaintext).encode()
    return base64_string(cipher.encrypt(plaintext_bytes))


def decrypt(cipher, ciphertext):
    return byte_to_str(cipher.decrypt(byte_string(ciphertext)))

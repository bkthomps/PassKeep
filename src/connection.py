import hashlib
import secrets
import sqlite3

from src import constants


def is_password_leaked(password):
    password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    db = sqlite3.connect(constants.DB_LEAKED_PASSWORDS)
    with db:
        entries = db.execute('SELECT password FROM leaked_passwords WHERE password = ?', (password,)).fetchone()
    return bool(entries)


def is_diceware_word(word):
    db = sqlite3.connect(constants.DB_DICEWARE_WORDS)
    with db:
        entries = db.execute('SELECT word FROM diceware WHERE word = ?', (word,)).fetchone()
    return bool(entries)


def get_random_diceware():
    random_id = 1 + secrets.randbelow(diceware_list_size())
    db = sqlite3.connect(constants.DB_DICEWARE_WORDS)
    with db:
        entries = db.execute('SELECT word FROM diceware WHERE id = ?', (random_id,)).fetchone()
    return entries[0]


def diceware_list_size():
    db = sqlite3.connect(constants.DB_DICEWARE_WORDS)
    with db:
        entries = db.execute('SELECT COUNT(word) FROM diceware').fetchone()
    return entries[0]


class Connection:
    def __init__(self):
        self._db = sqlite3.connect(constants.DB_PASSKEEP)

    def query(self, statement, arguments):
        with self._db:
            entries = self._db.execute(statement, arguments).fetchone()
        return entries

    def query_all(self, statement, arguments):
        with self._db:
            entries = self._db.execute(statement, arguments).fetchall()
        return entries

    def execute(self, statement, arguments):
        with self._db:
            entries = self._db.execute(statement, arguments)
        return entries.lastrowid

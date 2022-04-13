import hashlib
import sqlite3


def is_password_leaked(password):
    password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    db = sqlite3.connect("leaked_passwords.db")
    c = db.cursor()
    c.execute("SELECT password FROM leaked_passwords WHERE password = ?", (password,))
    entries = c.fetchone()
    c.close()
    return bool(entries)


class Connection:
    def __init__(self, username):
        self._username = username
        self._crypt_key = None
        self._db = sqlite3.connect('passkeep.db')

    def query(self, statement, arguments):
        c = self._db.cursor()
        c.execute(statement, arguments)
        entries = c.fetchone()
        c.close()
        return entries

    def query_all(self, statement, arguments):
        c = self._db.cursor()
        c.execute(statement, arguments)
        entries = c.fetchall()
        c.close()
        return entries

    def execute(self, statement, arguments):
        c = self._db.cursor()
        c.execute(statement, arguments)
        self._db.commit()
        c.close()

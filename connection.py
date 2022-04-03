import sqlite3


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

import sqlite3

from src.constants import DB_DICEWARE_WORDS

if __name__ == '__main__':
    # Long wordlist from https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
    file_name = 'diceware.txt'
    db = sqlite3.connect(DB_DICEWARE_WORDS)
    with open(file_name) as file:
        with db:
            for line in file:
                strings = line.split('	')
                word = strings[1].replace('-', '').rstrip('\n')
                db.execute('INSERT INTO diceware (word) VALUES (?)', (word,))

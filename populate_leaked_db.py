import os
import sqlite3

from src.constants import DB_LEAKED_PASSWORDS

MIN_FREQUENCY_TO_STORE = 100

if __name__ == '__main__':
    file_name = 'leaked_passwords.txt'  # From: https://haveibeenpwned.com/Passwords
    file_size = os.stat(file_name).st_size
    average_bytes_per_password = 44
    password_count = file_size / average_bytes_per_password
    db = sqlite3.connect(DB_LEAKED_PASSWORDS)
    with open(file_name) as file:
        added_count = 0
        line_count = 0
        with db:
            for line in file:
                line_count += 1
                if line_count % 10_000_000 == 0:
                    print('  {:.1f}% complete'.format(line_count * 100 / password_count))
                strings = line.split(':')
                password = strings[0]
                occurrences = int(strings[1].rstrip('\n'))
                if occurrences < MIN_FREQUENCY_TO_STORE:
                    continue
                added_count += 1
                db.execute('INSERT INTO leaked_passwords (password) VALUES (?)', (password,))
    print('Done adding passwords (added {} million)'.format(added_count / 1_000_000))

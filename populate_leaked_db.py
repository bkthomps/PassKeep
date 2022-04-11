import os
import sqlite3
import sys
from pathlib import Path

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('The call argument should path of the directory containing the .txt files of leaked passwords.')
    result = list(Path(sys.argv[1]).rglob('*.txt'))
    result = sorted(result, key=lambda x: os.stat(x).st_size)
    db = sqlite3.connect('leaked_passwords.db')
    file_count = 0
    for path in result:
        file_count += 1
        with open(path) as file:
            print('On file {} of {}: {}'.format(file_count, len(result), path))
            line_count = 0
            try:
                for line in file:
                    password = line.rstrip('\n')
                    line_count += 1
                    if line_count % 100_000 == 0:
                        print('  on line {:.1f} million'.format(line_count / 1_000_000))
                    c = db.cursor()
                    c.execute('INSERT OR IGNORE INTO leaked_passwords (password) VALUES (?)', (password,))
                    db.commit()
                    c.close()
            except UnicodeDecodeError:
                print('  failed file decoding')
    print('Done adding passwords')

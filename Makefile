.DEFAULT_GOAL := setup

setup:
	python3 -m pip install --upgrade pip -r requirements.txt
	sqlite3 passkeep.db < initdb.sql

create_passwords_db:
	rm -f leaked_passwords.db
	sqlite3 leaked_passwords.db < initdb_leaked.sql
	python3 populate_leaked_db.py
	rm -rf dir
	mkdir dir
	tar cvzf - leaked_passwords.db | split -b 40m - dir/leaked_passwords.tar.gz.

create_diceware_db:
	rm -f diceware.db
	sqlite3 diceware.db < initdb_diceware.sql
	python3 populate_diceware.py

extract_passwords_db:
	cat dir/leaked_passwords.tar.gz.* | tar xzvf -

test:
	pytest tst -n auto

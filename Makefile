.DEFAULT_GOAL := setup

setup: setup_passwords_db extract_leaked_db
	@echo "\n\n\n\n\n##############################\n\n"
	@echo "You can add the following line to your bashrc or zshrc:"
	@echo "\n"
	@echo "alias pass=\"pushd && cd $(PWD) && python3 -m pass && popd\""
	@echo "\n"
	@echo "Then source your bashrc or zshrc"
	@echo "\n\n##############################\n\n"

setup_passwords_db:
	if [ -f passkeep.db ]; then \
		mv passkeep.db passkeep_backup_$(shell date +%Y-%m-%dT%H:%M:%S).db; \
	fi
	python3 -m pip install --upgrade pip -r requirements.txt
	sqlite3 passkeep.db < initdb.sql

extract_leaked_db:
	cat dir/leaked_passwords.tar.gz.* | tar xzvf -

create_leaked_db:
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

delete_backups:
	rm -rf passkeep_backup_*.db

test:
	pytest tst -n auto

coverage:
	python3 -m pip install pytest-codecov
	pytest tst --cov=./ --cov-report=xml

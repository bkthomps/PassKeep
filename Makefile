.DEFAULT_GOAL := setup

setup:
	python3 -m pip install --upgrade pip -r requirements.txt
	sqlite3 passkeep.db < initdb.sql

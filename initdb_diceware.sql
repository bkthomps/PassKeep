/**
 * To setup the database, run: sqlite3 diceware.db < initdb_diceware.sql
 */

DROP TABLE IF EXISTS leaked_passwords;

CREATE TABLE diceware (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(9) NOT NULL
);

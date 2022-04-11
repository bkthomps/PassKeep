/**
 * To setup the database, run: sqlite3 leaked_passwords.db < initdb_leaked.sql
 */

DROP TABLE IF EXISTS leaked_passwords;

CREATE TABLE leaked_passwords (
    password VARCHAR(50) PRIMARY KEY
);

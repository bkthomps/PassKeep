/**
 * To setup the database, run: sqlite3 passkeep.db < initdb.sql
 */

DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS vault;

CREATE TABLE account (
    username    VARCHAR(50) PRIMARY KEY,
    auth_hashed VARCHAR(50) NOT NULL,
    auth_salt   VARCHAR(50) NOT NULL,
    crypt_salt  VARCHAR(50) NOT NULL,
    modified    DATETIME    NOT NULL,
    created     DATETIME    NOT NULL
);

CREATE TABLE vault (
    id           INTEGER      PRIMARY KEY AUTOINCREMENT,
    username     VARCHAR(50)  NOT NULL,
    iv           VARCHAR(25)  NOT NULL,
    account_name VARCHAR(250) NOT NULL,
    password     VARCHAR(250) NOT NULL,
    description  VARCHAR(500) NOT NULL,
    modified     DATETIME     NOT NULL,
    created      DATETIME     NOT NULL,
    FOREIGN KEY (username) REFERENCES account(username) ON DELETE CASCADE
);

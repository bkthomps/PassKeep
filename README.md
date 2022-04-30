[![GitHubBuild](https://github.com/bkthomps/PassKeep/workflows/build/badge.svg)](https://github.com/bkthomps/PassKeep)

# PassKeep
Open-source local password manager which uses PBKDF2 hashing with random salts to store account passwords, and
AES encryption in CBC mode to encrypt vault information.

## Utility
The user can create accounts and save vaults to those accounts. Each account is accessed by creating a username and a
password, which can later be changed. Each account can contain vaults which each have a name, description, and password.
The account password is salted and hashed, and the name, description, and password of each vault is encrypted.

Password checking for minimum length is performed as well as checking a corpus of previously-breaches passwords for
preventing account creation of weak passwords, and warning on vault creation with weak passwords.

Random password generation and diceware password generation is a provided utility, as well as strength checking of
random passwords and diceware passwords.

## Cryptographic Implementation
Whenever the user creates an account, the password is normalized and that normalized password is considered the main
key. In addition, a secret key of 32 cryptographically random bytes is created. A cryptographically random salt of 32
bytes is then created and used to get the hash of the main key using PBKDF2 with 250 000 iterations. The hashed main key
and the secret key are then combined by applying the xor on each bit to produce the auth key, and the previously
generated salt is the auth salt. Furthermore, 32 more cryptographically random bytes are created which will be
considered the crypt salt, and the same  hashing algorithm is applied with the main key to derive the crypt hash. The
secret key is saved to the keychain of the computer, and the username, auth key, auth salt, and crypt salt are saved
to the local database. The crypt key is required to encrypt and decrypt vault information, and thus is not stored. The
auth key is stored for verification that the password is correct when the user wishes to perform a further action
requiring authentication.

Whenever the user wishes to perform a command that requires authentication, they must provide the password, which will
be normalized to create the main key. The secret key will be retrieved from the computer's keychain. The crypt key will
then be generated using the crypt salt which is in the database by applying the PBDKF2 algorithm with 250 000 iterations
onto the provided man key and crypt salt and then applying an xor on each bit of that with the secret key. The same will
be done to retrieve the auth key but by using the auth salt. The auth key will then be retrieved from the database to
verify that the password was correct. This auth key has no cryptographic value in encrypting and decrypting vault
passwords or the crypt key, and is only used for failing fast by letting the user know that the password is incorrect.
The auth key and salt would produce gibberish if a malicious user were to try and use it to decrypt vault passwords.

Whenever the user wishes to create a vault, the information is encrypted using AES in CBC mode with a cryptographically
random initialization vector. The initialization vector and encrypted fields are then stores to the database. Whenever
the user wishes to retrieve vault information, the crypt key (which is generated from the main key and secret key) and
initialization vector is used to decrypt the vault information.

KEYRING_KEY = 'bkthomps-passkeep'

DB_LEAKED_PASSWORDS = 'leaked_passwords.db'
DB_DICEWARE_WORDS = 'diceware.db'
DB_PASSKEEP = 'passkeep.db'

USERNAME_MAX_LENGTH = 40
PASSWORD_MIN_LENGTH = 8

GENERATE_PASSWORD_MAX_LENGTH = 250
GENERATE_DICEWARE_MAX_WORDS = 12

SALT_SIZE = 32
HASH_ROUNDS = 250_000

ENTROPY_PER_CATEGORY = 25
ENTROPY_CATEGORIES = ['very bad', 'bad', 'reasonable', 'good', 'very good', 'excellent', 'outstanding']

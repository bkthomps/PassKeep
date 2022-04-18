from dataclasses import dataclass
from datetime import datetime

from Crypto.Cipher import AES

from src import utils


class VaultException(Exception):
    pass


class Vaults:
    @dataclass
    class VaultData:
        id: int
        iv: object
        description: str
        password: str

    def __init__(self, username, db, crypt_key):
        self._username = username
        self._db = db
        self._crypt_bytes = utils.byte_string(crypt_key)
        self._vaults = self._get_vaults()

    def _get_vaults(self):
        vaults = {}
        statement = 'SELECT id, iv, vault_name, description, password FROM vault WHERE username = ?'
        rows = self._db.query_all(statement, (self._username,))
        for row in rows:
            (vault_id, vault_iv, encrypted_vault_name, encrypted_description, encrypted_password) = row
            cipher = AES.new(self._crypt_bytes, AES.MODE_CBC, iv=vault_iv)
            vault_name = utils.byte_to_str(cipher.decrypt(utils.byte_string(encrypted_vault_name)))
            description = utils.byte_to_str(cipher.decrypt(utils.byte_string(encrypted_description)))
            password = utils.byte_to_str(cipher.decrypt(utils.byte_string(encrypted_password)))
            vault_data = self.VaultData(id=vault_id, iv=vault_iv, description=description, password=password)
            vaults[vault_name] = vault_data
        return vaults

    def _get_vault(self, vault_name):
        if vault_name not in self._vaults:
            raise VaultException('vault "{}" does not exist for this user'.format(vault_name))
        return self._vaults[vault_name]

    def get_vault_names(self):
        vault_names = []
        for key in self._vaults.keys():
            vault_names.append(key)
        vault_names.sort()
        return vault_names

    def get_vault_data(self, vault_name):
        vault = self._get_vault(vault_name)
        return vault.description, vault.password

    def add_vault(self, name, description, password):
        if name in self._vaults:
            raise VaultException('vault "{}" already exists for this user'.format(name))
        vault_name_bytes = utils.zero_pad(name).encode()
        description_bytes = utils.zero_pad(description).encode()
        password_bytes = utils.zero_pad(password).encode()
        cipher = AES.new(self._crypt_bytes, AES.MODE_CBC)
        iv = cipher.IV
        encrypted_vault_name = utils.base64_string(cipher.encrypt(vault_name_bytes))
        encrypted_description = utils.base64_string(cipher.encrypt(description_bytes))
        encrypted_password = utils.base64_string(cipher.encrypt(password_bytes))
        now = datetime.now()
        vault_id = self._db.execute(
            'INSERT INTO vault (iv, username, vault_name, description, password, modified, created) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (iv, self._username, encrypted_vault_name, encrypted_description, encrypted_password, now, now)
        )
        vault_data = self.VaultData(id=vault_id, iv=iv, description=description, password=password)
        self._vaults[name] = vault_data

    def delete_vault(self, vault_name):
        vault = self._get_vault(vault_name)
        self._db.execute('DELETE FROM vault WHERE id = ?', (vault.id,))
        self._vaults.pop(vault_name)

    def edit_vault_name(self, vault_name, new_name):
        vault = self._get_vault(vault_name)
        if new_name in self._vaults:
            raise VaultException('vault "{}" already exists for this user'.format(new_name))
        self._edit_vault(vault, new_name, vault.description, vault.password)
        self._vaults.pop(vault_name)
        self._vaults[new_name] = vault

    def edit_vault_description(self, vault_name, new_description):
        vault = self._get_vault(vault_name)
        self._edit_vault(vault, vault_name, new_description, vault.password)
        vault.description = new_description

    def edit_vault_password(self, vault_name, new_password):
        vault = self._get_vault(vault_name)
        self._edit_vault(vault, vault_name, vault.description, new_password)
        vault.password = new_password

    def _edit_vault(self, vault, new_name, new_description, new_password):
        vault_name_bytes = utils.zero_pad(new_name).encode()
        description_bytes = utils.zero_pad(new_description).encode()
        password_bytes = utils.zero_pad(new_password).encode()
        cipher = AES.new(self._crypt_bytes, AES.MODE_CBC, iv=vault.iv)
        encrypted_vault_name = utils.base64_string(cipher.encrypt(vault_name_bytes))
        encrypted_description = utils.base64_string(cipher.encrypt(description_bytes))
        encrypted_password = utils.base64_string(cipher.encrypt(password_bytes))
        self._db.execute('UPDATE vault SET vault_name = ?, description = ?, password = ? WHERE id = ?',
                         (encrypted_vault_name, encrypted_description, encrypted_password, vault.id))

    def update_vaults_crypt(self, crypt_key):
        self._crypt_bytes = utils.byte_string(crypt_key)
        for vault_name, vault in self._vaults.items():
            self._edit_vault(vault, vault_name, vault.description, vault.password)

    def update_username(self, username):
        self._username = username

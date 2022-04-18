import argparse
import getpass
import math
import random
import secrets
import string
import pyperclip

from src.account import Account
from src.account import AccountException
from src.connection import diceware_list_size
from src.connection import is_diceware_word
from src.connection import is_password_leaked
from src.connection import get_random_diceware
from src.constants import GENERATE_DICEWARE_MAX_WORDS
from src.constants import GENERATE_PASSWORD_MAX_LENGTH
from src.vaults import VaultException


class InputException(Exception):
    pass


def signup(args):
    username = args.username
    password = getpass.getpass('User Password:')
    confirm_password = getpass.getpass('Confirm Password:')
    Account.signup(username, password, confirm_password)


def _login(args):
    username = args.username
    password = getpass.getpass('User Password:')
    return Account.login(username, password)


def _confirm(text):
    number = random.randint(100, 999)
    print('To confirm {}, enter {}'.format(text, number))
    confirm = input('Confirmation:')
    if str(number) != confirm:
        raise InputException('input does not match confirmation')


def edit_username(args):
    account = _login(args)
    new_username = input('New Username:')
    account.edit_username(new_username)


def edit_password(args):
    account = _login(args)
    password = getpass.getpass('User Password:')
    confirm_password = getpass.getpass('Confirm Password:')
    account.edit_password(password, confirm_password)


def delete_user(args):
    account = _login(args)
    _confirm('deletion of user "{}"'.format(args.name))
    account.delete_user()


def vaults(args):
    account = _login(args)
    if not account.vaults:
        print('No vaults associated with this user')
        return
    print('The vaults for this user are:')
    for vault in account.vaults.get_vault_names():
        print('  {}'.format(vault))


def get_vault(args):
    account = _login(args)
    (description, password) = account.vaults.get_vault_data(args.name)
    print('Account Name: ' + args.name)
    print('Description: ' + description)
    print('The password has been copied to your clipboard.')
    pyperclip.copy(password)


def add_vault(args):
    account = _login(args)
    description = input('Vault Description:')
    password = getpass.getpass('Vault Password:')
    account.vaults.add_vault(args.name, description, password)
    if is_password_leaked(password):
        print('Warning: Password is part of a public data leak, consider changing it')


def delete_vault(args):
    account = _login(args)
    _confirm('deletion of vault "{}"'.format(args.name))
    account.vaults.delete_vault(args.name)


def edit_vault_name(args):
    account = _login(args)
    vault_name = input('New Vault Name:')
    account.vaults.edit_vault_name(args.name, vault_name)


def edit_vault_description(args):
    account = _login(args)
    description = input('New Description:')
    account.vaults.edit_vault_description(args.name, description)


def edit_vault_password(args):
    account = _login(args)
    vault_password = getpass.getpass('New Vault Password:')
    account.vaults.edit_vault_description(args.name, vault_password)
    if is_password_leaked(vault_password):
        print('Warning: Password is part of a public data leak, consider changing it')


def generate(args):
    if args.length <= 0:
        raise InputException('length must be a positive integer')
    if args.length > GENERATE_PASSWORD_MAX_LENGTH:
        raise InputException('max password length is {} characters'.format(GENERATE_PASSWORD_MAX_LENGTH))
    characters = ''
    if not args.no_special:
        characters += string.punctuation
    if not args.no_digit:
        characters += string.digits
    if not args.no_upper:
        characters += string.ascii_uppercase
    if not args.no_lower:
        characters += string.ascii_lowercase
    if not characters:
        raise InputException('no characters in permitted set')
    password = ''
    for i in range(args.length):
        random_index = secrets.randbelow(len(characters))
        password += characters[random_index]
    print('The random password has been copied to your clipboard.')
    pyperclip.copy(password)


def diceware(args):
    if args.words <= 0:
        raise InputException('words must be a positive integer')
    if args.words > GENERATE_DICEWARE_MAX_WORDS:
        raise InputException('max words length is {} words'.format(GENERATE_DICEWARE_MAX_WORDS))
    if args.separator not in string.punctuation:
        raise InputException('separator is not a special character')
    words = []
    for _ in range(args.words):
        words.append(get_random_diceware())
    password = args.separator.join(words)
    print('The diceware password has been copied to your clipboard.')
    pyperclip.copy(password)


def strength(args):
    password = getpass.getpass('Password:')
    entropy = _entropy(password)
    if entropy < 25:
        print('This is a very weak password')
    elif entropy < 50:
        print('This is a weak password')
    elif entropy < 75:
        print('This is a reasonable password')
    elif entropy < 100:
        print('This is a strong password')
    else:
        print('This is a very strong password')


def _entropy(password):
    (is_diceware, size) = _is_diceware(password)
    if is_diceware:
        entropy = _entropy_diceware(size)
        print('This diceware password has an entropy of {:.2f}'.format(entropy))
    else:
        entropy = _entropy_random(password)
        print('If this password is randomly-generated, it has an entropy of {:.2f}'.format(entropy))
    return entropy


def _is_diceware(password):
    delimiter = None
    for c in password:
        if c in string.punctuation:
            if delimiter and delimiter != c:
                return False, 0
            delimiter = c
    if not delimiter:
        return False, 0
    words = password.split(delimiter)
    for word in words:
        if not is_diceware_word(word):
            return False, 0
    return True, len(words)


def _entropy_diceware(size):
    return math.log2(diceware_list_size() ** size)


def _entropy_random(password):
    character_sets = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]
    all_characters = ''.join(character_sets)
    used = set()
    char_set_size = 0
    for c in password:
        if c in all_characters:
            for char_set in character_sets:
                if c in char_set and char_set not in used:
                    char_set_size += len(char_set)
                    used.add(char_set)
            continue
        if c not in used:
            char_set_size += 1
            used.add(c)
    return math.log2(char_set_size ** len(password))


def main():
    parser = argparse.ArgumentParser(prog='pk',
                                     usage='%(prog)s [options] path',
                                     description='An open-source local password manager.')
    subparsers = parser.add_subparsers()

    parser_signup = subparsers.add_parser('signup', help='Create a new account.')
    parser_signup.add_argument('--username', '-u', type=str, required=True)
    parser_signup.set_defaults(func=signup)

    parser_delete = subparsers.add_parser('delete', help='Delete an new account.')
    parser_delete.add_argument('--username', '-u', type=str, required=True)
    parser_delete.set_defaults(func=delete_user)

    parser_edit = subparsers.add_parser('edit', help='Edit user information.')
    parser_edit_subparsers = parser_edit.add_subparsers()

    parser_edit_username = parser_edit_subparsers.add_parser('username', help='Change the username for a user.')
    parser_edit_username.add_argument('--username', '-u', type=str, required=True)
    parser_edit_username.set_defaults(func=edit_username)

    parser_edit_password = parser_edit_subparsers.add_parser('password', help='Change the password for a user.')
    parser_edit_password.add_argument('--username', '-u', type=str, required=True)
    parser_edit_password.set_defaults(func=edit_password)

    parser_vaults = subparsers.add_parser('vaults', help='Access an existing account.')
    parser_vaults.add_argument('--username', '-u', type=str, required=True)
    parser_vaults.set_defaults(func=vaults)

    parser_vault = subparsers.add_parser('vault', help='Operate on a vault.')
    parser_vault_subparsers = parser_vault.add_subparsers()

    parser_get_vault = parser_vault_subparsers.add_parser('get', help='Get an existing vault.')
    parser_get_vault.add_argument('--username', '-u', type=str, required=True)
    parser_get_vault.add_argument('--name', '-n', type=str, required=True)
    parser_get_vault.set_defaults(func=get_vault)

    parser_add_vault = parser_vault_subparsers.add_parser('add', help='Add a new vault.')
    parser_add_vault.add_argument('--username', '-u', type=str, required=True)
    parser_add_vault.add_argument('--name', '-n', type=str, required=True)
    parser_add_vault.set_defaults(func=add_vault)

    parser_delete_vault = parser_vault_subparsers.add_parser('delete', help='Delete an existing vault.')
    parser_delete_vault.add_argument('--username', '-u', type=str, required=True)
    parser_delete_vault.add_argument('--name', '-n', type=str, required=True)
    parser_delete_vault.set_defaults(func=delete_vault)

    parser_edit_vault = parser_vault_subparsers.add_parser('edit', help='Edit an existing vault.')
    parser_edit_vault_subparsers = parser_edit_vault.add_subparsers()

    parser_edit_vault_name = parser_edit_vault_subparsers.add_parser('name', help='Edit the name of a vault.')
    parser_edit_vault_name.add_argument('--username', '-u', type=str, required=True)
    parser_edit_vault_name.add_argument('--name', '-n', type=str, required=True)
    parser_edit_vault_name.set_defaults(func=edit_vault_name)

    parser_edit_vault_desc = parser_edit_vault_subparsers.add_parser('desc', help='Edit the description of a vault.')
    parser_edit_vault_desc.add_argument('--username', '-u', type=str, required=True)
    parser_edit_vault_desc.add_argument('--name', '-n', type=str, required=True)
    parser_edit_vault_desc.set_defaults(func=edit_vault_description)

    parser_edit_vault_pass = parser_edit_vault_subparsers.add_parser('password', help='Edit the password of a vault.')
    parser_edit_vault_pass.add_argument('--username', '-u', type=str, required=True)
    parser_edit_vault_pass.add_argument('--name', '-n', type=str, required=True)
    parser_edit_vault_pass.set_defaults(func=edit_vault_password)

    parser_generate = subparsers.add_parser('gen', help='Randomly generate a password.')
    parser_generate.add_argument('--length', '-l', type=int, default=25)
    parser_generate.add_argument('--no-special', action='store_true')
    parser_generate.add_argument('--no-digit', action='store_true')
    parser_generate.add_argument('--no-upper', action='store_true')
    parser_generate.add_argument('--no-lower', action='store_true')
    parser_generate.set_defaults(func=generate)

    parser_diceware = subparsers.add_parser('dice', help='Generate a password using the diceware wordlist.')
    parser_diceware.add_argument('--words', '-w', type=int, default=6)
    parser_diceware.add_argument('--separator', '-sep', type=str, default='.')
    parser_diceware.set_defaults(func=diceware)

    parser_strength = subparsers.add_parser('strength', help='Get the strength of a password.')
    parser_strength.set_defaults(func=strength)

    arguments = parser.parse_args()
    if getattr(arguments, 'func', None):
        try:
            arguments.func(arguments)
        except (InputException, AccountException, VaultException) as e:
            print('Error: ' + str(e))
        except KeyboardInterrupt:
            pass
    else:
        parser.print_help()

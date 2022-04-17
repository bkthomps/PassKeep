import argparse
import getpass
import math
import secrets
import string

import pyperclip

from account import Account
from account import AccountException
from connection import is_password_leaked


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


def vaults(args):
    account = _login(args)
    account_vaults = account.get_vaults()
    if len(account_vaults) == 0:
        print('No vaults associated with this user')
        return
    print('The vaults for this user are:')
    account_vaults.sort(key=lambda x: x[0])
    for vault in account_vaults:
        print('  {}'.format(vault[0]))


def get_vault(args):
    account = _login(args)
    account_vaults = account.get_vaults()
    for vault_data in account_vaults:
        if vault_data[0] == args.name:
            (description, password) = account.get_vault(vault_data)
            print('Account Name: ' + vault_data[0])
            print('Description: ' + description)
            print('The password has been copied to your clipboard.')
            pyperclip.copy(password)
            return
    raise InputException('vault name not found')


def add_vault(args):
    account = _login(args)
    description = input('Vault Description:')
    password = getpass.getpass('Vault Password:')
    account.add_vault(args.name, description, password)
    if is_password_leaked(password):
        print('Warning: Password is part of a public data leak, consider changing it')


def generate(args):
    max_length = 250
    if args.length <= 0:
        raise InputException('length must be a positive integer')
    if args.length > max_length:
        raise InputException('max password length is {} characters'.format(max_length))
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
    print('The password has been copied to your clipboard.')
    pyperclip.copy(password)


def strength(args):
    password = getpass.getpass('Password:')
    entropy = _entropy(password)
    print('Your password has an entropy of {:.2f}'.format(entropy))
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pk',
                                     usage='%(prog)s [options] path',
                                     description='An open-source local password manager.')
    subparsers = parser.add_subparsers()

    parser_signup = subparsers.add_parser('signup', help='Create a new account.')
    parser_signup.add_argument('--username', '-u', type=str, required=True)
    parser_signup.set_defaults(func=signup)

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

    parser_generate = subparsers.add_parser('gen', help='Randomly generate a password.')
    parser_generate.add_argument('--length', '-l', type=int, default=25)
    parser_generate.add_argument('--no-special', action='store_true')
    parser_generate.add_argument('--no-digit', action='store_true')
    parser_generate.add_argument('--no-upper', action='store_true')
    parser_generate.add_argument('--no-lower', action='store_true')
    parser_generate.set_defaults(func=generate)

    parser_diceware = subparsers.add_parser('gen', help='Generate a password using the diceware wordlist.')
    parser_diceware.add_argument('--words', '-w', type=int, default=6)
    parser_diceware.set_defaults(func=diceware)

    parser_strength = subparsers.add_parser('strength', help='Get the strength of a password.')
    parser_strength.set_defaults(func=strength)

    arguments = parser.parse_args()
    if getattr(arguments, 'func', None):
        try:
            arguments.func(arguments)
        except (InputException, AccountException) as e:
            print('Error: ' + str(e))
        except KeyboardInterrupt:
            pass
    else:
        parser.print_help()

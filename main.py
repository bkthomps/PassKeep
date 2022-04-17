import argparse
import getpass
import secrets
import string

import pyperclip

from account import Account
from account import AccountException
from connection import is_password_leaked


def signup(args):
    username = args.username
    password = getpass.getpass('User Password:')
    confirm_password = getpass.getpass('Confirm Password:')
    try:
        Account.signup(username, password, confirm_password)
    except AccountException as e:
        print('Error: ' + str(e))


def _login(args):
    username = args.username
    password = getpass.getpass('User Password:')
    return Account.login(username, password)


def vaults(args):
    try:
        account = _login(args)
        account_vaults = account.get_vaults()
        if len(account_vaults) == 0:
            print('No vaults associated with this user')
            return
        print('The vaults for this user are:')
        account_vaults.sort(key=lambda x: x[0])
        for vault in account_vaults:
            print('  {}'.format(vault[0]))
    except AccountException as e:
        print('Error: ' + str(e))


def get_vault(args):
    try:
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
        print('Error: Vault name not found')
    except AccountException as e:
        print('Error: ' + str(e))


def add_vault(args):
    try:
        account = _login(args)
        description = input('Vault Description:')
        password = getpass.getpass('Vault Password:')
        account.add_vault(args.name, description, password)
        if is_password_leaked(password):
            print('Warning: Password is part of a public data leak, consider changing it')
    except AccountException as e:
        print('Error: ' + str(e))


def generate(args):
    max_length = 250
    if args.length <= 0:
        print('Error: length must be a positive integer')
        return
    if args.length > max_length:
        print('Error: max password length is {} characters'.format(max_length))
        return
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
        print('Error: no characters in permitted set')
        return
    password = ''
    for i in range(args.length):
        random_index = secrets.randbelow(len(characters))
        password += characters[random_index]
    print('The password has been copied to your clipboard.')
    pyperclip.copy(password)


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

    parser_generate = subparsers.add_parser('gen', help='Generate a password.')
    parser_generate.add_argument('--length', '-l', type=int, default=25)
    parser_generate.add_argument('--no-special', action='store_true')
    parser_generate.add_argument('--no-digit', action='store_true')
    parser_generate.add_argument('--no-upper', action='store_true')
    parser_generate.add_argument('--no-lower', action='store_true')
    parser_generate.set_defaults(func=generate)

    arguments = parser.parse_args()
    if getattr(arguments, 'func', None):
        arguments.func(arguments)
    else:
        parser.print_help()

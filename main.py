import argparse
import getpass

import pyperclip

from account import Account
from account import AccountException
from account import signup as account_signup


def signup(args):
    username = args.username
    password = getpass.getpass('Password:')
    confirm_password = getpass.getpass('Confirm Password:')
    try:
        account_signup(username, password, confirm_password)
    except AccountException as e:
        print('Error: ' + str(e))


def _login(args):
    username = args.username
    password = getpass.getpass('Password:')
    return Account.login(username, password)


def vaults(args):
    try:
        account = _login(args)
        account_vaults = account.get_vaults()
        if len(account_vaults) == 0:
            print('No vaults associated with this user')
        for vault in account_vaults:
            print('Id: {}, Name: {}'.format(vault[0], vault[1]))
    except AccountException as e:
        print('Error: ' + str(e))


def get_vault(args):
    try:
        account = _login(args)
        vault = account.get_vault(args.id)
        print('Account Name: ' + vault[0])
        print('Description: ' + vault[1])
        print('The password has been copied to your clipboard.')
        pyperclip.copy(vault[2])
    except AccountException as e:
        print('Error: ' + str(e))


def add_vault(args):
    try:
        account = _login(args)
        description = input("Vault Description:")
        password = getpass.getpass('Vault Password:')
        account.add_vault(args.name, description, password)
    except AccountException as e:
        print('Error: ' + str(e))


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
    parser_get_vault.add_argument('--id', '-i', type=int, required=True)
    parser_get_vault.set_defaults(func=get_vault)

    parser_add_vault = parser_vault_subparsers.add_parser('add', help='Add a new vault.')
    parser_add_vault.add_argument('--username', '-u', type=str, required=True)
    parser_add_vault.add_argument('--name', '-n', type=str, required=True)
    parser_add_vault.set_defaults(func=add_vault)

    arguments = parser.parse_args()
    if getattr(arguments, "func", None):
        arguments.func(arguments)
    else:
        print('Not a valid argument')

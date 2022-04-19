class UserInputException(Exception):
    pass


class AccountException(UserInputException):
    pass


class VaultException(AccountException):
    pass

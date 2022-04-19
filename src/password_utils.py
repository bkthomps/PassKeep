import math
import secrets
import string

from src import connection


def random_password(character_set, length):
    password = ''
    for i in range(length):
        random_index = secrets.randbelow(len(character_set))
        password += character_set[random_index]
    return password


def random_diceware(separator, length):
    words = []
    for _ in range(length):
        words.append(connection.get_random_diceware())
    return separator.join(words)


class Password:
    def __init__(self, password):
        (self.is_diceware, word_count) = self._is_diceware(password)
        if self.is_diceware:
            self.entropy = Password._entropy_diceware(word_count)
        else:
            self.entropy = Password._entropy_random(password)

    @staticmethod
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
            if not connection.is_diceware_word(word):
                return False, 0
        return True, len(words)

    @staticmethod
    def _entropy_diceware(word_count):
        return math.log2(connection.diceware_list_size() ** word_count)

    @staticmethod
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

import string

from src import password_utils


class TestEntropy:
    def _rounded_entropy(self, password):
        password = password_utils.Password(password)
        assert self.expected_diceware == password.is_diceware
        return round(password.entropy, 1)

    def test_random_passwords(self):
        self.expected_diceware = False
        assert 00.0 == self._rounded_entropy('')
        assert 32.0 == self._rounded_entropy('[-tyZ')
        assert 65.5 == self._rounded_entropy('m2`?9KzLA,')
        assert 98.3 == self._rounded_entropy('f75^aD<:V[sY4;$')
        assert 131.1 == self._rounded_entropy('.[Ma]|Gx?,tIR2x^3JSA')
        assert 163.9 == self._rounded_entropy('6@g|PtLfs2)/8^vZDOU#]QDB.')
        assert 51.7 == self._rounded_entropy('scn7f19lms')
        assert 57.0 == self._rounded_entropy('WCtlxJrlyu')
        assert 59.5 == self._rounded_entropy('9IvklHqK4Y')
        assert 47.0 == self._rounded_entropy('bhclepcjqs')
        assert 19.9 == self._rounded_entropy('862575')
        assert 13.3 == self._rounded_entropy('5149')

    def test_diceware_passwords(self):
        self.expected_diceware = True
        assert 25.8 == self._rounded_entropy('lather.busybody')
        assert 38.8 == self._rounded_entropy('wisplike.conflict.follow')
        assert 51.7 == self._rounded_entropy('visible.mobile.aflutter.squint')
        assert 64.6 == self._rounded_entropy('cinema.igloo.concept.porridge.virtual')
        assert 77.5 == self._rounded_entropy('sadly.gotten.bonnet.breezy.mulberry.scorch')
        assert 25.8 == self._rounded_entropy('lather-busybody')


class TestGenerateRandom:
    @staticmethod
    def _generate_password(character_set, length):
        password = password_utils.random_password(character_set, length)
        password_data = password_utils.Password(password)
        return round(password_data.entropy, 1)

    def test_digits(self):
        character_set = string.digits
        assert 33.2 == self._generate_password(character_set, 10)
        assert 83.0 == self._generate_password(character_set, 25)
        assert 166.1 == self._generate_password(character_set, 50)

    def test_lowercase(self):
        character_set = string.ascii_lowercase
        assert 47.0 == self._generate_password(character_set, 10)
        assert 117.5 == self._generate_password(character_set, 25)
        assert 235.0 == self._generate_password(character_set, 50)

    def test_uppercase(self):
        character_set = string.ascii_uppercase
        assert 47.0 == self._generate_password(character_set, 10)
        assert 117.5 == self._generate_password(character_set, 25)
        assert 235.0 == self._generate_password(character_set, 50)

    def test_letters(self):
        character_set = string.ascii_letters
        assert 142.5 == self._generate_password(character_set, 25)
        assert 285.0 == self._generate_password(character_set, 50)
        assert 427.5 == self._generate_password(character_set, 75)

    def test_letters_digits(self):
        character_set = string.ascii_letters + string.digits
        assert 297.7 == self._generate_password(character_set, 50)
        assert 446.6 == self._generate_password(character_set, 75)
        assert 595.4 == self._generate_password(character_set, 100)

    def test_letters_digits_punctuation(self):
        character_set = string.ascii_letters + string.digits + string.punctuation
        assert 491.6 == self._generate_password(character_set, 75)
        assert 655.5 == self._generate_password(character_set, 100)


class TestGenerateDiceware:
    def test_smoke(self):
        for i in range(12):
            length = i + 1
            used = set()
            count = min(3 * length, 15)
            for _ in range(count):
                password = password_utils.random_diceware('.', length)
                assert password not in used
                used.add(password)
                assert length == len(password.split('.'))
                for c in password:
                    if c != '.':
                        assert c in string.ascii_lowercase

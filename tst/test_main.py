from src.main import _entropy


class TestEntropy:
    @staticmethod
    def _rounded_entropy(password):
        return round(_entropy(password), 1)

    def test_random_passwords(self):
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
        assert 25.8 == self._rounded_entropy('lather.busybody')
        assert 38.8 == self._rounded_entropy('wisplike.conflict.follow')
        assert 51.7 == self._rounded_entropy('visible.mobile.aflutter.squint')
        assert 64.6 == self._rounded_entropy('cinema.igloo.concept.porridge.virtual')
        assert 77.5 == self._rounded_entropy('sadly.gotten.bonnet.breezy.mulberry.scorch')
        assert 25.8 == self._rounded_entropy('lather-busybody')

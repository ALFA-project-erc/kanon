import pytest

from histropy.units.errors import IllegalBaseValueError
from histropy.units.radices import Historical, RadixBase


class TestRadixBase:

    def test_bases(self):
        with pytest.raises(ValueError):
            RadixBase([1], [2], "Sexagesimal")
        assert Historical('2r 7s 29; 45') == 339.75
        with pytest.raises(IllegalBaseValueError):
            Historical((-6, 3), ())
        with pytest.raises(IllegalBaseValueError):
            Historical((11, 10, 10), ())

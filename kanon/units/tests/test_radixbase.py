import pytest

from kanon.units import RadixBase, radix_registry


class TestRadixBase:
    def test_bases(self):
        test_radix = RadixBase([1], [2], "Test", "a")

        assert "Test" in radix_registry
        assert radix_registry["Test"].base is test_radix

        assert test_radix.mixed

        with pytest.raises(ValueError):
            RadixBase([1], [2], "Sexagesimal")

        with pytest.raises(ValueError):
            RadixBase([11, 5], [2], "a", integer_separators=["a", "b", "c"])

        with pytest.raises(AssertionError):
            RadixBase([], [2], "n1")
        with pytest.raises(AssertionError):
            RadixBase([1], [1.1], "n1")

    def test_get(self):

        sexa_base = radix_registry["Sexagesimal"].base

        assert sexa_base[1] == 60
        assert sexa_base[-1] == 60
        assert sexa_base[100] == 60

        histo_base = radix_registry["Historical"].base
        assert histo_base[-2:1] == [10, 12, 30]

        with pytest.raises(ValueError):
            histo_base[5:]
        with pytest.raises(ValueError):
            histo_base[:3]

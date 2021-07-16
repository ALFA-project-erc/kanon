import numpy as np
import pytest
from astropy.table.column import Column

from kanon.tables.hcolumn import HColumn
from kanon.units import Historical, Sexagesimal


class TestHColumn:
    def test_init(self):

        col = HColumn([1, 2, 3])

        assert col.significant is None

        with pytest.raises(AttributeError):
            assert col.ceil()

        bcol = col.astype(Sexagesimal)

        with pytest.raises(ValueError) as err:
            bcol[1] = 3

        assert "Sexagesimal" in str(err.value)

        assert "Sexagesimal" in repr(bcol)
        assert repr(col)[2:] == repr(Column(col))[1:]

    def test_astype(self):
        col = HColumn([1, 2, 3])

        bcol = col.astype(Sexagesimal)

        assert bcol.basedtype == Sexagesimal
        assert not bcol.attrs_equal(col)

        reconverted = bcol.astype(int)
        assert reconverted.attrs_equal(col)
        assert reconverted.basedtype is None

        assert np.array_equal(col.astype(float).astype(Sexagesimal), bcol)
        assert np.array_equal(bcol.astype(Historical), bcol)

        with pytest.raises(ValueError):
            strcol = HColumn(["a", "b", "c"])
            strcol.astype(Sexagesimal)

    def test_truncable(self):
        bcol = HColumn([1, 2, 3]).astype(Sexagesimal)

        assert bcol.significant == 0

        bcol = bcol.resize(2)
        bcol += Sexagesimal(31) >> 2

        assert bcol.significant == 2

        assert np.array_equal(
            [
                Sexagesimal("1;1"),
                Sexagesimal("2;1"),
                Sexagesimal("3;1"),
            ],
            bcol.ceil(1),
        )
        assert np.array_equal([1, 2, 3], bcol.truncate(0))
        assert np.array_equal(
            [
                Sexagesimal("1;0"),
                Sexagesimal("2;0"),
                Sexagesimal("3;0"),
            ],
            bcol.floor(1),
        )
        assert np.array_equal(
            [
                Sexagesimal("1;1"),
                Sexagesimal("2;1"),
                Sexagesimal("3;1"),
            ],
            round(bcol, 1),
        )

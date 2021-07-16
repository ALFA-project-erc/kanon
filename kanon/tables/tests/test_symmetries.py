import pandas as pd
import pytest

from kanon.tables.symmetries import (
    OutOfBoundsOriginError,
    OverlappingSymmetryError,
    Symmetry,
)


class TestSymmetry:
    def test_init(self):
        with pytest.raises(ValueError):
            Symmetry("a")

    def test_symmetry_call(self):
        symmirror = Symmetry("mirror", sign=-1)
        symperiod = Symmetry("periodic")

        df = pd.DataFrame()

        assert symmirror(df).equals(df)

        df = pd.DataFrame({"a": [1, 2, 4], "b": [4, 5, 6]}).set_index("a")

        symdf = symmirror(df)

        assert len(symdf) == 2 * len(df) - 1

        assert list(symdf.index) == [1, 2, 4, 6, 7]

        symdf = symperiod(df)

        assert len(symdf) == 2 * len(df)

        with pytest.raises(ValueError):
            Symmetry("mirror", source=(2, 1))

        sym = Symmetry("periodic", source=(0, 1))
        with pytest.raises(OutOfBoundsOriginError):
            sym(df)

        sym = Symmetry("periodic", targets=[1])
        with pytest.raises(OverlappingSymmetryError):
            sym(df)

        sym = Symmetry("periodic", source=(1, 2), targets=[5])
        assert sym(df).index[-1] == 6

    def test_mirror_multi_targets(self):
        sym = Symmetry("mirror", targets=[10, 15])
        df = pd.DataFrame({"a": [2, 3, 5], "b": [7, 6, 9]}).set_index("a")

        res = df.pipe(sym)

        assert len(res) == 9

        assert list(res.index) == [2, 3, 5, 10, 12, 13, 15, 17, 18]
        assert list(res["b"]) == [7, 6, 9, 9, 6, 7, 9, 6, 7]

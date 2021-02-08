import pandas as pd
import pytest

from histropy.tables.symmetries import (OutOfBoundsOriginError,
                                        OverlappingSymmetryError, Symmetry)


class TestSymmetry:

    def test_symmetric_df(self):
        symmirror = Symmetry("mirror", sign=-1)
        symperiod = Symmetry("periodic")

        df = pd.DataFrame()

        assert symmirror.symmetric_df(df).equals(df)

        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}).set_index("a")

        symdf = symmirror.symmetric_df(df)

        assert len(symdf) == 2 * len(df) - 1

        symdf = symperiod.symmetric_df(df)

        assert len(symdf) == 2 * len(df)

        with pytest.raises(ValueError):
            Symmetry("mirror", origin=(2, 1))

        sym = Symmetry("periodic", origin=(0, 1))
        with pytest.raises(OutOfBoundsOriginError):
            sym.symmetric_df(df)

        sym = Symmetry("periodic", target=[1])
        with pytest.raises(OverlappingSymmetryError):
            sym.symmetric_df(df)

        sym = Symmetry("periodic", origin=(1, 2), target=[5])
        assert sym.symmetric_df(df).index[-1] == 6

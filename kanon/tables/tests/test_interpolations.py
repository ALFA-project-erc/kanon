import hypothesis.strategies as st
import numpy as np
import pandas as pd
from hypothesis.core import given

from kanon.tables.interpolations import (linear_interpolation,
                                         quadratic_interpolation)


def build_dataframe():
    return pd.DataFrame([5, 4, 6, 12], [1, 5, 7, 8])


class TestInterpolations:

    @given(st.floats(allow_infinity=False, allow_nan=False, min_value=1, max_value=8))
    def test_linear(self, key: float):
        df = build_dataframe()

        np_interp = np.interp(key, np.array(df.index), np.array(df[0]))

        assert linear_interpolation(df, key) == np_interp

    def test_quadratic(self):
        df = build_dataframe()

        assert quadratic_interpolation(df, 1.25) == 4.7421875
        assert np.isclose(quadratic_interpolation(df, 10), 34)

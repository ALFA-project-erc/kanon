import hypothesis.strategies as st
import numpy as np
import pandas as pd
import pytest
from hypothesis.core import given

from kanon.tables.interpolations import (
    distributed_interpolation,
    linear_interpolation,
    quadratic_interpolation,
)


def build_dataframe():
    return pd.DataFrame([5, 4, 6, 12], [1, 5, 7, 8])


class TestInterpolations:
    @given(st.floats(allow_infinity=False, allow_nan=False, min_value=1, max_value=8))
    def test_linear_hypothesis(self, key: float):
        df = build_dataframe()

        np_interp = np.interp(key, np.array(df.index), np.array(df[0]))

        assert linear_interpolation(df, key) == np_interp

    def test_linear(self):
        df = build_dataframe()

        assert linear_interpolation(df, -1) == 5.5
        assert linear_interpolation(df, 9) == 18

    def test_quadratic(self):
        df = build_dataframe()

        assert quadratic_interpolation(df, 1.25) == 4.7421875
        assert np.isclose(quadratic_interpolation(df, 10), 34)

    def test_distributed(self):
        df = pd.DataFrame([5] + [np.nan] * 8 + [45], list(range(6, 16)))

        convex = df.pipe(distributed_interpolation, direction="convex")
        assert list(convex[0]) == [5, 9, 13, 17, 21, 25, 30, 35, 40, 45]
        concave = df.pipe(distributed_interpolation, direction="concave")
        assert list(concave[0]) == [5, 10, 15, 20, 25, 29, 33, 37, 41, 45]

        df = pd.DataFrame([5] + [np.nan] * 6 + [45], [i / 4 for i in range(8)])
        concave = df.pipe(distributed_interpolation, direction="concave")
        assert len(concave) == 8 and not np.isnan(concave[0]).any()

        df = pd.DataFrame(
            [5] + [np.nan] * 6 + [45] + [np.nan] * 6 + [100], [i / 4 for i in range(15)]
        )
        concave = df.pipe(distributed_interpolation, direction="concave")
        assert len(concave) == 15 and not np.isnan(concave[0]).any()

        with pytest.raises(ValueError) as err:
            df = pd.DataFrame([5] + [np.nan] * 8 + [45], list(range(6, 15)) + [31])
            df.pipe(distributed_interpolation, direction="convex")
        assert str(err.value) == "The DataFrame must have regular steps"

        with pytest.raises(ValueError) as err:
            df = pd.DataFrame([5] + [np.nan] * 9, list(range(6, 16)))
            df.pipe(distributed_interpolation, direction="convex")
        assert str(err.value) == "The DataFrame must start and end with non nan values"

        with pytest.raises(ValueError) as err:
            df.pipe(distributed_interpolation, direction="unknown")
        assert "unknown" in str(err.value)

        from kanon.units import Sexagesimal

        df = pd.DataFrame(
            [Sexagesimal(5)] + [np.nan] * 8 + [Sexagesimal(45)], list(range(6, 16))
        )

        convex = df.pipe(distributed_interpolation, direction="convex")
        assert list(convex[0]) == [5, 9, 13, 17, 21, 25, 30, 35, 40, 45]

        df = pd.DataFrame(
            [Sexagesimal("0;0,5")] + [np.nan] * 8 + [Sexagesimal("0;0,45")],
            list(range(6, 16)),
        )

        convex = df.pipe(distributed_interpolation, direction="convex")
        assert list(convex[0]) == [
            Sexagesimal.from_int(x).shift(2)
            for x in [5, 9, 13, 17, 21, 25, 30, 35, 40, 45]
        ]
        assert convex.index[0].dtype == "int64"

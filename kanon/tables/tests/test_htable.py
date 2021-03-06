from math import isclose
from typing import Tuple

import hypothesis.strategies as st
import numpy as np
import pytest
from hypothesis import assume
from hypothesis.core import given

from kanon.tables.htable import HTable
from kanon.tables.symmetries import Symmetry


class TestHTable:

    sample = {"a": [1, 2, 3, 4], "b": [5, 9, 12, 15]}

    def test_init(self):

        table = HTable(self.sample)
        assert table[2]["b"] == 12

        with pytest.raises(IndexError):
            table.get(3)

        table.add_index("b")
        assert table.get(5) == 1

    gen_table_strategy = st.builds(
        HTable,
        st.lists(
            st.tuples(
                st.integers(min_value=int(-1e15), max_value=int(1e15)),
                st.floats(allow_nan=False, allow_infinity=False, width=16)
            ), min_size=1, unique_by=(lambda x: x[0])
        ).map(lambda x: list(zip(*sorted(x)))),
        names=st.just(("A", "B")),
        index=st.just("A")
    )

    @given(gen_table_strategy)
    def test_symmetry(self, tab: HTable):
        assume(len(tab) > 1)
        tab.symmetry = [Symmetry("mirror", sign=-1)]
        df = tab.to_pandas()
        assert df["B"].iloc[0] == -df["B"].iloc[-1]
        tab.symmetry = [Symmetry("periodic")]
        df = tab.to_pandas()
        assert df["B"].iloc[0] == df["B"].iloc[len(tab)]

    @given(gen_table_strategy.flatmap(
        lambda x: st.tuples(st.floats(
            min_value=float(min(x["A"])),
            max_value=float(max(x["A"])),
            allow_nan=False
        ), st.just(x))))
    def test_interpolation(self, hypo: Tuple[float, HTable]):
        key, tab = hypo
        fres = np.interp(key, [float(x) for x in tab.columns[0]], [float(x) for x in tab.columns[1]])
        sres = tab.get(key)
        assert isclose(fres, float(sres), abs_tol=1e9)

        with pytest.raises(IndexError):
            tab.get(tab[0]["A"] - 1)

    def test_apply(self):
        tab = HTable(self.sample, index="a")

        assert np.array_equal(
            tab.apply("b", lambda x: x + 2)["b"],
            np.add(tab["b"], np.array([2] * len(tab)))
        )

        tab_float = tab.apply("b", lambda x: x + 0.3)
        assert tab_float["b"].dtype == np.dtype("float64")
        tab_int = tab_float.apply("b", round)
        assert tab_int["b"].dtype == np.dtype("int64")

    def test_index(self):
        tab = HTable(self.sample, index="a")

        assert tab.loc[1]["b"] == 5
        with pytest.raises(KeyError):
            tab.loc[5]

        new_tab = tab.copy(set_index="b")
        assert new_tab.loc[5]["a"] == 1
        with pytest.raises(KeyError):
            new_tab.loc[1]

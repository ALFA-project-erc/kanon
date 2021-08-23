from math import isclose
from typing import Tuple

import astropy.units as u
import hypothesis.strategies as st
import numpy as np
import pandas as pd
import pytest
from astropy.table import setdiff
from astropy.table.operations import join
from astropy.units.core import UnitConversionError
from hypothesis import assume
from hypothesis.core import given

from kanon.tables.htable import HTable, join_multiple
from kanon.tables.symmetries import Symmetry

sample = {"a": [1, 2, 3, 4, 5], "b": [5, 9, 12, 25, 26]}


def make_sample_table(index="a"):
    return HTable(sample, index=index)


def test_init():

    table = HTable(sample)
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
            st.floats(allow_nan=False, allow_infinity=False, width=16),
        ),
        min_size=2,
        unique_by=(lambda x: x[0]),
    ).map(lambda x: list(zip(*sorted(x)))),
    names=st.just(("A", "B")),
    index=st.just("A"),
)


@given(gen_table_strategy)
def test_symmetry(tab: HTable):
    assume(len(tab) > 1)
    tab.symmetry = [Symmetry("mirror", sign=-1)]
    df = tab.to_pandas()
    assert df["B"].iloc[0] == -df["B"].iloc[-1]
    tab.symmetry = [Symmetry("periodic")]
    df = tab.to_pandas()
    assert df["B"].iloc[0] == df["B"].iloc[len(tab)]


@given(
    gen_table_strategy.flatmap(
        lambda x: st.tuples(
            st.floats(
                min_value=float(min(x["A"])),
                max_value=float(max(x["A"])),
                allow_nan=False,
            ),
            st.just(x),
        )
    )
)
def test_interpolation(hypo: Tuple[float, HTable]):
    key, tab = hypo
    fres = np.interp(
        key, [float(x) for x in tab.columns[0]], [float(x) for x in tab.columns[1]]
    )
    sres = tab.get(key)
    assert isclose(fres, float(sres), abs_tol=1e9)


def test_apply():
    tab = make_sample_table()

    assert np.array_equal(
        tab.apply("b", lambda x: x + 2)["b"],
        np.add(tab["b"], np.array([2] * len(tab))),
    )

    tab_float = tab.apply("b", lambda x: x + 0.3)
    assert tab_float["b"].dtype == np.dtype("float64")
    tab_int = tab_float.apply("b", round, "rounded")
    assert tab_int["rounded"].dtype == np.dtype("int64")

    def tostr(x):
        return f"{x}a"

    tab_str = tab.apply("b", tostr)
    assert tab_str["b"].dtype.char == "U"


def test_index():
    tab = make_sample_table()

    assert tab.loc[1]["b"] == 5
    with pytest.raises(KeyError):
        tab.loc[6]

    new_tab = tab.copy(set_index="b")
    assert new_tab.loc[5]["a"] == 1
    with pytest.raises(KeyError):
        new_tab.loc[1]


def test_populate():
    tab = make_sample_table(index="b")

    pop_array = [i for i in range(5, 15)]

    populated = tab.populate(pop_array, method="interpolate")

    assert len(populated) == len(set(populated["b"]).union(pop_array))

    assert populated.loc[6]["a"] == tab.get(6)


def test_diff():
    tab = make_sample_table()

    assert list(tab.diff()["b"]) == [0, 4, 3, 13, 1]
    assert list(tab.diff(prepend=[3])["b"]) == [2, 4, 3, 13, 1]
    assert list(tab.diff(append=[24])["b"]) == [4, 3, 13, 1, -2]

    with pytest.raises(ValueError):
        tab.diff(prepend=[1, 1])


def test_fill():
    tab = make_sample_table()
    tab["b"] = tab["b"].astype("float64")

    tab = tab.populate([i / 4 for i in range(4, 16)])

    tab_filled = tab.fill("distributed_convex", (2, 4))
    assert list(tab_filled.loc[3:4]["b"]) == [12, 15, 18, 21, 25]

    tab_filled = tab.fill("distributed_concave", (2, 4))
    assert list(tab_filled.loc[3:4]["b"]) == [12, 16, 19, 22, 25]

    tab_unmasked = tab.filled(50)

    assert (
        len(setdiff(tab_unmasked, tab.fill("distributed_convex", (4, 5)).filled(50)))
        == 0
    )
    assert (
        len(
            setdiff(tab_unmasked, tab.fill("distributed_convex", (3.5, 3.5)).filled(50))
        )
        == 0
    )

    def fill_50(df: pd.DataFrame):
        return df.fillna(50)

    assert len(setdiff(tab_unmasked, tab.fill(fill_50))) == 0

    with pytest.raises(ValueError) as err:
        tab.fill("distributed_convex", (2.5, 4))
    assert str(err.value) == "First and last rows must not be masked"

    with pytest.raises(ValueError) as err:
        tab.fill("not a method", (2, 4))
    assert str(err.value) == "Incorrect fill method"


def test_join_multiple():
    data = [HTable({"a": x, "b": x}) for x in [[1, 2, 3], [8, 10, 13], [435, 13, 3.5]]]
    multiple_joined = join_multiple(*data, join_type="outer")
    single_joined = join(
        join(data[0], data[1], join_type="outer"), data[2], join_type="outer"
    )

    assert len(setdiff(multiple_joined, single_joined)) == 0


def test_plot():
    tab = make_sample_table()
    plot = tab.plot2d(".")
    assert len(plot) == 1
    assert plot[0].get_marker() == "."


def test_get_with_quantity():
    tab = make_sample_table()

    tab["a"].unit = u.degree

    assert tab.get(3) == 12
    assert tab.get(3 * u.degree) == 12

    assert tab.get(180 * u.arcmin) == 12

    with pytest.raises(UnitConversionError):
        assert tab.get(3 * u.deg_C)

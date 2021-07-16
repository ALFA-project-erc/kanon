import json
import math
from math import isclose
from typing import Tuple

import astropy.units as u
import hypothesis.strategies as st
import numpy as np
import pytest
import requests_mock
from astropy.units.quantity import Quantity
from astropy.utils.data import get_pkg_data_filename
from hypothesis.core import given

from kanon.tables import HTable
from kanon.tables.htable_reader import DISHAS_REQUEST_URL
from kanon.units import Sexagesimal


class TestBasedHTable:
    @requests_mock.Mocker(kw="mock")
    def test_read(self, **kwargs):

        kwargs["mock"].get(requests_mock.ANY, json={"error": "Non existing id"})

        path = get_pkg_data_filename("data/table_content-180.json")
        with open(path, "r") as f:
            content = json.load(f)
        kwargs["mock"].get(DISHAS_REQUEST_URL.format(180), json=content)

        table: HTable = HTable.read(180, format="dishas")

        assert table["Mean Argument of the Sun"].unit is u.degree
        assert table["Mean Argument of the Sun"].basedtype is Sexagesimal
        assert table["Entries"].significant == 2

        assert table.loc[Sexagesimal(1)] == table[0]

        assert table.loc[Sexagesimal(3)]["Entries"].equals(Sexagesimal("-00 ; 06,27"))

        assert table.loc[Sexagesimal(3)]["Entries"].equals(
            table.get(Sexagesimal(3), with_unit=False)
        )

        assert len(table.symmetry) == 1
        sym = table.symmetry[0]

        assert table.get(1) == -table.get(37)

        assert sym.symtype == "mirror"

        assert "Sexagesimal" in repr(table)

        with pytest.raises(FileNotFoundError):
            HTable.read(181, format="dishas")

    gen_table_strategy = st.builds(
        HTable,
        st.lists(
            st.tuples(
                st.from_type(Sexagesimal).map(lambda x: x.resize(2).truncate()),
                st.from_type(Sexagesimal).map(lambda x: x.resize(2).truncate()),
            ),
            min_size=2,
            max_size=7,
            unique_by=(lambda x: x[0]),
        ).map(lambda x: list(zip(*sorted(x)))),
        names=st.just(("A", "B")),
        index=st.just("A"),
        dtype=st.just([object, object]),
    )

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
    def test_interpolation(self, hypo: Tuple[float, HTable]):
        key, tab = hypo
        fres = np.interp(
            key, [float(x) for x in tab.columns[0]], [float(x) for x in tab.columns[1]]
        )
        sres = tab.get(key)
        assert isclose(fres, float(sres), abs_tol=1e9)

    @given(gen_table_strategy)
    def test_quantity(self, tab: HTable):
        tab["A"].unit = u.degree
        tab["B"].unit = u.degree

        value = tab.get(tab["A"][0])

        assert isinstance(value, Quantity)
        assert value.unit is u.degree
        assert isinstance(value.value, Sexagesimal)

    @given(gen_table_strategy)
    def test_loc_slice(self, tab: HTable):
        sliced = tab.loc[tab["A"][1] :]
        assert not isinstance(sliced, HTable) or len(sliced) == len(tab) - 1

    def test_based_fill(self):
        sin_table = HTable(
            [
                list(Sexagesimal.range(91)),
                [
                    round(Sexagesimal.from_float(math.sin(x * math.pi / 180), 3))
                    for x in range(91)
                ],
            ],
            names=("Arg", "Val"),
            index="Arg",
        )
        sin_table_grid = sin_table[
            [i for i in range(91) if i <= 60 and i % 12 == 0 or i > 60 and i % 6 == 0]
        ]
        sin_table_pop_euclidean = sin_table_grid.populate(list(Sexagesimal.range(91)))
        sin_table_pop_euclidean.fill("distributed_convex")

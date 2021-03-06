import json
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
from kanon.tables.htable import DISHAS_REQUEST_URL
from kanon.units import Sexagesimal


class TestBasedHTable:

    @requests_mock.Mocker(kw="mock")
    def test_read(self, **kwargs):
        path = get_pkg_data_filename('data/table_content-180.json')
        with open(path, "r") as f:
            content = json.load(f)
        kwargs["mock"].get(DISHAS_REQUEST_URL.format(180), json=content)

        table: HTable = HTable.read(180, format="dishas")

        assert table["Mean Argument of the Sun"].unit is u.degree

        assert table.loc[Sexagesimal("1")] == table[0]

        assert table.loc[Sexagesimal("3")]["Entries"].equals(Sexagesimal(6, 27, sign=-1))

        kwargs["mock"].get(DISHAS_REQUEST_URL.format(181), json={})

        with pytest.raises(FileNotFoundError):
            HTable.read(181, format="dishas")

    gen_table_strategy = st.builds(
        HTable,
        st.lists(
            st.tuples(
                st.from_type(Sexagesimal).map(lambda x: x.resize(2).truncate()),
                st.from_type(Sexagesimal).map(lambda x: x.resize(2).truncate())
            ), min_size=1, unique_by=(lambda x: x[0])
        ).map(lambda x: list(zip(*sorted(x)))),
        names=st.just(("A", "B")),
        index=st.just("A"),
        dtype=st.just([object, object])
    )

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

    @given(gen_table_strategy)
    def test_quantity(self, tab: HTable):
        tab["A"].unit = u.degree
        tab["B"].unit = u.degree

        value = tab.get(tab["A"][0])

        assert isinstance(value, Quantity)
        assert value.unit is u.degree
        assert isinstance(value.value, Sexagesimal)

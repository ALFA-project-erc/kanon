import json
from math import isclose
from pathlib import Path
from typing import Tuple, Type

import hypothesis.strategies as st
import numpy as np
import requests_mock
from hypothesis.core import given

from histropy.tables.htable import DISHAS_REQUEST_URL, HTable
from histropy.units import BasedReal, Sexagesimal

Sexagesimal: Type[BasedReal]


class TestHTable:
    @requests_mock.Mocker(kw="mock")
    def test_read(self, **kwargs):
        path = Path(__file__).parent / 'data/table_content-180.json'
        with open(path, "r") as f:
            content = json.load(f)
        kwargs["mock"].get(DISHAS_REQUEST_URL.format(180), json=content)

        table: HTable = HTable.read(180, format="dishas")

        assert table.loc[Sexagesimal(1)] == table[0]

        assert table.loc[3][1] is Sexagesimal(6, 27, sign=-1)

    gen_table_strategy = st.builds(
        HTable,
        st.lists(
            st.tuples(st.from_type(Sexagesimal), st.from_type(Sexagesimal)),
            min_size=1, unique_by=(lambda x: x[0])
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
    def test_hypo(self, hypo: Tuple[float, HTable]):
        key, tab = hypo
        fres = np.interp(key, [float(x) for x in tab.columns[0]], [float(x) for x in tab.columns[1]])
        sres = tab.get(key)
        assert isclose(fres, float(sres), abs_tol=1e9)
        assert isclose(Sexagesimal.from_float(fres, 1), sres, abs_tol=1e9)

    def test_interpolation(self):
        args = [1, 2, 3, 5, 9]
        entries = [5, 62, 1, -6, -2]
        table = HTable([args, entries], names=("Arg 1", "Entries"), index=("Arg 1"))

        assert table.get(1.5) == 33.5
        assert table.get(4) == -2.5
        assert table.get(6) == -5
        assert table.get(5.3) == -5.7

        table = HTable([
            [Sexagesimal.from_int(x) for x in args],
            [Sexagesimal.from_int(x) for x in entries]
        ], names=("Arg 1", "Entries"), index=("Arg 1"))

        assert table.get(Sexagesimal.from_float(1.5, 1)) == 33.5
        assert table.get(4) == -2.5
        assert table.get(6) == -5
        assert table.get(Sexagesimal.from_float(5.3, 1)) == -5.7

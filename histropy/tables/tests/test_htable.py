import json
from pathlib import Path
from typing import Type

import requests_mock

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

    def test_interpolation(self):
        table = HTable([[1, 2, 3, 5, 9], [5, 62, 1, -6, -2]], names=("Arg 1", "Entries"), index=("Arg 1"))

        assert table.get(1.5) == 33.5
        assert table.get(4) == -2.5
        assert table.get(6) == -5

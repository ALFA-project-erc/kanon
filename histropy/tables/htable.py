from typing import Generic, List

import pandas as pd
from astropy.io import registry
from astropy.table import Table

import histropy.units.radices as rad
from histropy.utils.types_helper import NT

from .interpolations import Interpolator, linear_interpolation


class HTable(Table, Generic[NT]):

    interpolate: Interpolator = staticmethod(linear_interpolation)

    def __init__(self, *args, **kwargs):
        index = kwargs.get("index")
        if index:
            del kwargs["index"]
        super().__init__(*args, **kwargs)
        if index:
            self.add_index(index)

        self.symmetry = None

        self.bounds = (float("-inf"), float("inf"))

    def add_symmetry(self, symmetry: str):
        pass

    def get(self, key: NT):

        df: pd.DataFrame = self.to_pandas(index=True)

        try:
            return self.loc[key]
        except KeyError:
            pass
        if self.bounds[0] < key < self.bounds[1]:
            low = df.truncate(after=key).iloc[-1]
            high = df.truncate(before=key).iloc[0]

            return self.interpolate((low.name, low[0]), (high.name, high[0]), key)

        else:
            raise NotImplementedError


DISHAS_REQUEST_URL = "https://dishas.obspm.fr?index=table_content&hits=true&id={}"


def read_table_dishas(requested_id: str) -> HTable:
    import requests

    res = requests.get(
        DISHAS_REQUEST_URL.format(int(requested_id)),
    ).json()
    if not res:
        raise FileNotFoundError(
            f'{requested_id} ID not found in DISHAS database')
    values = res["value_original"]

    def read_sexag_array(array: List[str]) -> rad.Sexagesimal:
        negative = array[0][0] == "-"
        return rad.Sexagesimal(*(abs(int(v)) for v in array), sign=-1 if negative else 1)

    args = [read_sexag_array(v["value"]) for v in values["args"]["argument1"]]
    entries = [read_sexag_array(v["value"]) for v in values["entry"]]

    return HTable[rad.Sexagesimal]([args, entries], names=("Arg 1", "Entries"), index=("Arg 1"), dtype=[object, object])


registry.register_reader("dishas", HTable, read_table_dishas)

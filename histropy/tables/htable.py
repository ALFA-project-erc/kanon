from numbers import Number
from typing import List, Tuple

from astropy.io import registry
from astropy.table import Table

from histropy.units.radices import BasedReal, RadixBase

Sexagesimal: BasedReal = RadixBase.name_to_base["sexagesimal"].type
DISHAS_REQUEST_URL = "https://dishas.obspm.fr?index=table_content&hits=true&id={}"


def linear_interpolation(x: Tuple[Number, Number], y: Tuple[Number, Number], t: Number):
    return (y[1] - x[1]) * (t - x[0]) / (y[0] - x[0])


class HTable(Table):

    interpolate = linear_interpolation

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

    def get(self, key: Sexagesimal):
        if self.bounds[0] > key < self.bounds[1]:
            pass


def read_table_dishas(requested_id):
    import requests

    res = requests.get(
        DISHAS_REQUEST_URL.format(int(requested_id)),
    ).json()
    if not res:
        raise FileNotFoundError(
            f'{requested_id} ID not found in DISHAS database')
    values = res["value_original"]

    def read_sexag_array(array: List[str]) -> Sexagesimal:
        negative = array[0][0] == "-"
        return Sexagesimal(*(abs(int(v)) for v in array), sign=-1 if negative else 1)

    args = [read_sexag_array(v["value"]) for v in values["args"]["argument1"]]
    entries = [read_sexag_array(v["value"]) for v in values["entry"]]

    return HTable([args, entries], names=("Arg 1", "Entries"), index=("Arg 1"), dtype=[object, object])


registry.register_reader("dishas", HTable, read_table_dishas)

from numbers import Number
from typing import Callable, Dict, Generic, List, Type, TypeVar

import pandas as pd
from astropy.io import registry
from astropy.table import Table

from histropy.units import Sexagesimal
from histropy.units.radices import BasedReal
from histropy.utils.types.dishas import NumberType, TableContent

from .interpolations import Interpolator, linear_interpolation

Sexagesimal: Type[BasedReal]

NT = TypeVar('NT', bound=Number)


class HTable(Table, Generic[NT]):

    def __init__(self, *args, **kwargs):
        index = kwargs.get("index")
        if index:
            del kwargs["index"]
        super().__init__(*args, **kwargs)
        if index:
            self.add_index(index)

        self.symmetry = None

        self.bounds = (float("-inf"), float("inf"))

        self.interpolate = linear_interpolation

    @property
    def interpolate(self) -> Interpolator:
        return self._interpolate

    @interpolate.setter
    def interpolate(self, func: Interpolator):
        self._interpolate = func

    def add_symmetry(self, symmetry: str):
        pass

    def get(self, key: Number) -> NT:
        """Get a value from any keys based on interpolated data

        :param key: Any argument for an interpolated function
        :type key: Number
        :raises IndexError: Key is out of bounds
        :return: Interpolated value
        :rtype: NT
        """

        try:
            return self.loc[key][1]
        except KeyError:
            pass

        if self.bounds[0] < key < self.bounds[1]:
            df: pd.DataFrame = self.to_pandas(index=True)
            df.index = df.index.map(float)

            return self.interpolate(df, key)

        else:
            raise NotImplementedError


DISHAS_REQUEST_URL = "https://dishas.obspm.fr/elastic-query?index=table_content&hits=true&id={}"


def read_table_dishas(requested_id: str) -> HTable:

    import requests

    res: TableContent = requests.get(
        DISHAS_REQUEST_URL.format(int(requested_id)),
    ).json()
    if not res:
        raise FileNotFoundError(
            f'{requested_id} ID not found in DISHAS database')
    values = res["value_original"]

    def read_sexag_array(array: List[str]) -> Sexagesimal:
        negative = array[0][0] == "-"
        return Sexagesimal(*(abs(int(v)) for v in array), sign=-1 if negative else 1)

    numberReader: Dict[NumberType, Callable[[List[str]], Number]] = {
        "sexagesimal": read_sexag_array
    }

    args = [numberReader[res["argument1_type_of_number"]](v["value"]) for v in values["args"]["argument1"]]
    entries = [numberReader[res["entry_type_of_number"]](v["value"]) for v in values["entry"]]

    return HTable(
        [args, entries],
        names=(res["argument1_name"], "Entries"),
        index=(res["argument1_name"]),
        dtype=[object, object]
    )


registry.register_reader("dishas", HTable, read_table_dishas)

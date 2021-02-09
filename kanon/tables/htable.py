from numbers import Number
from typing import Callable, Dict, List, Type, Union

import astropy.units as u
import pandas as pd
from astropy.io import registry
from astropy.table import Table
from astropy.table.table import TableAttribute

from kanon.units import Sexagesimal
from kanon.units.radices import BasedReal
from kanon.utils.types.dishas import NumberType, TableContent, UnitType

from .interpolations import Interpolator, linear_interpolation
from .symmetries import Symmetry

__all__ = ["HTable"]


Sexagesimal: Type[BasedReal]


class HTable(Table):

    _interpolator: Interpolator = TableAttribute(default=linear_interpolation)

    def __init__(self, *args, index=None, symmetry: List[Symmetry] = [], **kwargs):
        super().__init__(*args, **kwargs)

        if index:
            self.add_index(index)

        self.symmetry = symmetry
        self.bounds = (float("-inf"), float("inf"))

    @property
    def interpolate(self) -> Interpolator:
        return self._interpolator

    @interpolate.setter
    def interpolate(self, func: Interpolator):
        self._interpolator = func

    def to_pandas(self, index=None, use_nullable_int=True, symmetry=True) -> pd.DataFrame:
        df = super().to_pandas(index=index, use_nullable_int=use_nullable_int)
        if symmetry:
            for sym in self.symmetry:
                df = df.pipe(sym)
        return df

    def get(self, key: Number, with_unit=True) -> Number:
        """Get a value from any keys based on interpolated data

        :param key: Any argument for an interpolated function
        :type key: Number
        :raises IndexError: Key is out of bounds
        :return: Interpolated value
        :rtype: NT
        """

        df = self.to_pandas()
        unit = (self.columns[1].unit if with_unit else 1) or 1
        try:
            return df.loc[float(key)][0] * unit
        except KeyError:
            pass

        if self.bounds[0] < key < self.bounds[1]:
            df.index = df.index.map(float)

            return self.interpolate(df, key) * unit

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

    def read_intsexag_array(array: List[str]) -> Union[Sexagesimal, int]:
        if len(array) == 1:
            return int(array[0])
        else:
            return (
                read_sexag_array(array[1:]) >> len(array) - 1
            ) + Sexagesimal.from_int(int(array[0][0]), len(array))

    number_reader: Dict[NumberType, Callable[[List[str]], Number]] = {
        "sexagesimal": read_sexag_array,
        "floating sexagesimal": read_sexag_array,
        "integer and sexagesimal": read_intsexag_array
    }

    unit_reader: Dict[UnitType, u.Unit] = {
        "degree": u.degree,
        "day": u.day
    }

    arg_types = (res["argument1_type_of_number"], res["argument1_number_unit"])
    entry_types = (res["entry_type_of_number"], res["entry_number_unit"])

    try:
        args = [number_reader.get(arg_types[0], lambda x:x)(v["value"]) for v in values["args"]["argument1"]]
        entries = [number_reader.get(entry_types[0], lambda x:x)(v["value"]) for v in values["entry"]]
    except ValueError:
        args = [v["value"] for v in values["args"]["argument1"]]
        entries = [v["value"] for v in values["entry"]]

    table = HTable(
        [args, entries],
        names=(res["argument1_name"], "Entries"),
        index=(res["argument1_name"]),
        dtype=[object, object]
    )

    table.columns[0].unit = unit_reader.get(arg_types[1])
    table.columns[1].unit = unit_reader.get(entry_types[1])

    return table


registry.register_reader("dishas", HTable, read_table_dishas)

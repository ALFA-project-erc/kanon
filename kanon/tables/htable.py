from numbers import Number
from typing import Callable, Dict, List, Optional, Type, Union

import numpy as np
import pandas as pd
from astropy.io import registry
from astropy.table import Table
from astropy.table.table import TableAttribute
from astropy.units import Quantity
from astropy.units.core import Unit

from kanon.utils.types.dishas import NumberType, TableContent, UnitType

from .interpolations import Interpolator, linear_interpolation
from .symmetries import Symmetry

__all__ = ["HTable"]


class HTable(Table):
    """`HTable` is a subclass of `astropy.table.Table`, made to model Historical Astronomy tables
    representing mathematical functions. Its argument column or columns are its index, while the
    values should be on the first column. Columns are allowed to contain all kinds of `~numbers.Number`,
    especially `~kanon.units.radices.BasedReal` numbers. `HTable` also provides additional historical
    features and metadata.

    See also: https://docs.astropy.org/en/stable/table/

    >>> table = HTable({"args": [1,2,3], "values": [5.1,3.9,4.3]}, index="args")
    >>> table
    <HTable length=3>
    args  values
    int64 float64
    ----- -------
        1     5.1
        2     3.9
        3     4.3
    >>> table.loc[2]
    <Row index=1>
    args  values
    int64 float64
    ----- -------
        2     3.9
    >>> table.loc[2]["values"]
    3.9

    :param data: Data to initialize table.
    :type data: Optional[Data]
    :param names: Specify column names.
    :type names: Optional[List[str]]
    :param index: Columns considered as the indices.
    :type index: Optional[Union[str, List[str]]]
    :param units: List or dict of units to apply to columns.
    :type units: Optional[List[Unit]]
    :param dtype: Specify column data types.
    :type dtype: Optional[List]
    :param symmetry: Specify a list of `~kanon.tables.Symmetry` on this table. Defaults to empty list.
    :type symmetry: Optional[List[Symmetry]]
    :param interpolate: Specify a custom interpolation method,\
    defaults to `~kanon.tables.interpolations.linear_interpolation`.
    :type interpolate: Optional[Interpolator]
    :param opposite: Defines if the table values should be of the opposite sign. Defaults to False.
    :type opposite: Optional[bool]

    """

    interpolate: Interpolator = TableAttribute(default=linear_interpolation)
    """Interpolation method."""
    symmetry: List[Symmetry] = TableAttribute(default=[])
    """Table symmetries."""
    opposite: bool = TableAttribute(default=False)
    """Defines if the table values should be of the opposite sign."""

    def __init__(self,
                 data=None,
                 names: Optional[List[str]] = None,
                 index: Optional[Union[str, List[str]]] = None,
                 dtype: Optional[List] = None,
                 units: Optional[List[Unit]] = None,
                 *args, **kwargs
                 ):

        super().__init__(data=data, names=names, units=units, dtype=dtype, *args, **kwargs)

        if index:
            self.add_index(index, unique=True)

    def to_pandas(self, index=None, use_nullable_int=True, symmetry=True) -> pd.DataFrame:
        if not self.indices and not index:
            raise IndexError("HTable should have an index, defining the function's arguments")
        df = super().to_pandas(index=index, use_nullable_int=use_nullable_int)
        if symmetry:
            for sym in self.symmetry:
                df = df.pipe(sym)
        return df

    def get(self, key: Number, with_unit=True) -> Union[Number, Quantity]:
        """Get the value from any key based on interpolated data.

        :param key: Argument for an interpolated function
        :type key: `~numbers.Number`
        :param with_unit: Whether the result is represented as a Quantity or not. \
        Defaults to `True`
        :type with_unit: bool
        :raises IndexError: Key is out of bounds
        :return: Interpolated value
        :rtype: `~numbers.Number`
        """

        df = self.to_pandas()

        unit = (self.columns[1].unit if with_unit else 1) or 1
        try:
            return df.loc[key][0] * unit
        except KeyError:
            pass

        return self.interpolate(df, key) * unit

    def apply(self, column: str, func: Callable) -> "HTable":
        table = self.copy()
        try:
            table[column] = func(table[column])
        except TypeError:
            table[column] = np.vectorize(func)(table[column])
        return table

    def set_index(self, index: Union[str, List[str]], engine=None):
        for c in self.colnames:
            self.remove_indices(c)

        self.add_index(index, unique=True, engine=engine)

    def copy(self, set_index=None, copy_data=True) -> "HTable":
        table: HTable = super().copy(copy_data=copy_data)
        if set_index:
            table.set_index(set_index)
        return table


DISHAS_REQUEST_URL = "https://dishas.obspm.fr/elastic-query?index=table_content&hits=true&id={}"


def read_table_dishas(requested_id: str) -> HTable:

    import astropy.units as u
    import requests

    from kanon.units import BasedReal, Sexagesimal

    Sexagesimal: Type[BasedReal]

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

    def read_intsexag_array(array: List[str]) -> Sexagesimal:
        if len(array) == 1:
            return Sexagesimal.from_int(int(array[0]))
        else:
            return (
                read_sexag_array(array[1:]) >> len(array) - 1
            ) + Sexagesimal.from_int(int(array[0][0]), len(array))

    number_reader: Dict[NumberType, Callable[[List[str]], Number]] = {
        "sexagesimal": read_sexag_array,
        "floating sexagesimal": read_sexag_array,
        "integer and sexagesimal": read_intsexag_array
    }

    unit_reader: Dict[UnitType, Unit] = {
        "degree": u.degree,
        "day": u.day
    }

    arg_types = (res["argument1_type_of_number"], res["argument1_number_unit"])
    entry_types = (res["entry_type_of_number"], res["entry_number_unit"])

    args = [number_reader.get(arg_types[0], lambda x:x)(v["value"]) for v in values["args"]["argument1"]]
    entries = [number_reader.get(entry_types[0], lambda x:x)(v["value"]) for v in values["entry"]]

    table = HTable(
        [args, entries],
        names=(res["argument1_name"], "Entries"),
        index=(res["argument1_name"]),
        units=[unit_reader.get(arg_types[1]), unit_reader.get(entry_types[1])],
        dtype=[object, object]
    )

    return table


registry.register_reader("dishas", HTable, read_table_dishas)

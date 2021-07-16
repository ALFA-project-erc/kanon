from functools import partial
from typing import (
    Callable,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

import numpy as np
import pandas as pd
from astropy.table import Row, Table
from astropy.table.operations import join
from astropy.table.pprint import TableFormatter
from astropy.table.table import TableAttribute
from astropy.units import Quantity
from astropy.units.core import Unit

from kanon.tables.hcolumn import HColumn, _patch_dtype_info_name
from kanon.utils.types.number_types import Real

from .interpolations import (
    Interpolator,
    distributed_interpolation,
    linear_interpolation,
)
from .symmetries import Symmetry

__all__ = ["HTable"]


T = TypeVar("T")


class GenericTableAttribute(TableAttribute, Generic[T]):
    def __get__(self, instance, owner) -> T:
        return super().__get__(instance, owner)


class HTableFormatter(TableFormatter):

    _pformat_col = _patch_dtype_info_name(TableFormatter._pformat_col, 1)


class HTable(Table):
    """`HTable` is a subclass of `astropy.table.Table`, made to model Historical Astronomy tables
    representing mathematical functions. Its argument column or columns are its index, while the
    values should be on the first column. Columns are allowed to contain all kinds of `~numbers.Real`,
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
    :type names: Union[List[str], Tuple[str, ...]]
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

    Column = HColumn
    TableFormatter = HTableFormatter

    interpolate = GenericTableAttribute[Interpolator](default=linear_interpolation)
    """Interpolation method."""
    symmetry: List[Symmetry] = TableAttribute(default=[])
    """Table symmetries."""
    opposite: bool = TableAttribute(default=False)
    """Defines if the table values should be of the opposite sign."""

    def __init__(
        self,
        data=None,
        names: Optional[Union[List[str], Tuple[str, ...]]] = None,
        index: Optional[Union[str, List[str]]] = None,
        dtype: Optional[List] = None,
        units: Optional[List[Unit]] = None,
        *args,
        **kwargs,
    ):

        super().__init__(
            data=data, names=names, units=units, dtype=dtype, *args, **kwargs
        )

        if index:
            self.set_index(index)

    def _check_index(self, index=None):
        if not self.indices and not index:
            raise IndexError(
                "HTable should have an index, defining the function's arguments"
            )
        return self.primary_key[0]

    def to_pandas(
        self, index=None, use_nullable_int=True, symmetry=True
    ) -> pd.DataFrame:
        self._check_index(index)
        df = super().to_pandas(index=index, use_nullable_int=use_nullable_int)
        if symmetry:
            for sym in self.symmetry:
                df = df.pipe(sym)
        return df

    @overload
    def get(self, key: Union[Real, Quantity], with_unit: Literal[False]) -> Real:
        ...

    @overload
    def get(self, key: Real, with_unit: Literal[True] = True) -> Union[Real, Quantity]:
        ...

    @overload
    def get(self, key: Quantity, with_unit: Literal[True] = True) -> Quantity:
        ...

    def get(self, key: Union[Real, Quantity], with_unit=True):
        """Get the value from any key based on interpolated data.

        :param key: Argument for an interpolated function
        :type key: `~numbers.Real`
        :param with_unit: Whether the result is represented as a Quantity or not. \
        Defaults to `True`
        :type with_unit: bool
        :raises IndexError: Key is out of bounds
        :return: Interpolated value
        :rtype: `~numbers.Real`
        """

        df = self.to_pandas()

        unit = (self.columns[self.values_column].unit if with_unit else 1) or 1

        val: Real

        if isinstance(key, int):
            val = float(key)

        elif isinstance(key, Quantity):
            val = key.to(self[self.primary_key[0]].unit).value

        else:
            val = key

        return self.interpolate(df, val) * unit

    def apply(
        self, column: str, func: Callable, new_name: Optional[str] = None
    ) -> "HTable":
        """
        Applies a function on a column and returns the new `HTable`

        :param column: Name of the column to be modified
        :param func: Function applied to the column
        :param new_name: New name for the modified column, optional
        :return: HTable with modified column
        :rtype: HTable
        """

        table = self.copy()
        try:
            table[column] = func(table[column])
        except (TypeError, AttributeError, ValueError):
            table[column] = np.vectorize(func)(table[column])

        if new_name:
            table.rename_columns([column], [new_name])

        return table

    def set_index(self, index: Union[str, List[str]], engine=None):
        for c in self.colnames:
            self.remove_indices(c)

        self.add_index(index, unique=True, engine=engine)

    @property
    def values_column(self) -> str:
        """
        Column representing the values
        """
        self._check_index()

        set_val = set(self.colnames) - set(self.primary_key)
        assert len(set_val) == 1, f"Values should be in 1 column, not {len(set_val)}"

        return list(set_val)[0]

    def copy(self, set_index=None, copy_data=True) -> "HTable":
        table: HTable = super().copy(copy_data=copy_data)
        if set_index:
            table.set_index(set_index)
        return table

    def populate(
        self, array: List[Real], method: Literal["mask", "interpolate"] = "mask"
    ) -> "HTable":
        """
        Populate a table with values from new keys contained in `array`.
        """

        key = self._check_index()

        right = {key: array}

        if method == "interpolate":
            right[self.values_column] = [self.get(x) for x in array]

        table: HTable = join(self, HTable(right), join_type="outer")

        table.set_index(key)

        return table

    def fill(
        self,
        method: Union[
            Literal["distributed_convex", "distributed_concave"],
            Callable[[pd.DataFrame], pd.DataFrame],
        ],
        bounds: Optional[Tuple[Real, Real]] = None,
    ) -> "HTable":
        """Fill masked values within `bounds` with the specified `method`.
        To fill with a unique value, see `~HTable.filled`.

        :param method: Method to use for filling masked values
        :type method: Literal["distributed_convex", "distributed_concave"]
        :param bounds: Tuple of arguments bounds, defaults to the whole table
        :type bounds: Optional[Tuple[Real, Real]], optional
        """

        slice_bounds = slice(*(bounds or (None, None)))

        filltab: HTable = self.loc[slice_bounds]

        if isinstance(filltab, Row):
            return self.copy()

        valcol = filltab[filltab.values_column]

        if valcol[0] is np.ma.masked or valcol[-1] is np.ma.masked:
            raise ValueError("First and last rows must not be masked")

        if np.ma.masked not in valcol:
            return self.copy()

        fill_method: Callable[[pd.DataFrame], pd.DataFrame]

        if method == "distributed_concave":
            fill_method = partial(distributed_interpolation, direction="concave")
        elif method == "distributed_convex":
            fill_method = partial(distributed_interpolation, direction="convex")
        elif callable(method):
            fill_method = method
        else:
            raise ValueError("Incorrect fill method")

        df = filltab.to_pandas().pipe(fill_method)

        tab_copy = self.copy()
        tab_copy.loc[slice_bounds] = HTable.from_pandas(df, index=True)

        if not np.ma.is_masked(tab_copy[tab_copy.values_column]):
            tab_copy[tab_copy.values_column] = HColumn(tab_copy[filltab.values_column])

        return tab_copy

    def diff(
        self, n=1, prepend: List = [], append: List = [], new_name: Optional[str] = None
    ) -> "HTable":
        """Applies `np.diff` on this table's column values to calculate the n-th difference.
        By default, it will prepend the first value.

        :return: HTable with n-th difference values.
        :rtype: HTable
        """

        cat = prepend + append
        if len(cat) > n or n > len(cat) > 0:
            raise ValueError(
                f"You must prepend or append exactly n ({n}) values or 0 values"
            )

        if len(cat) == 0:
            prepend = [self[0][self.values_column]] * n

        kwargs = {}
        if prepend:
            kwargs["prepend"] = prepend
        if append:
            kwargs["append"] = append

        diff = partial(np.diff, n=n, **kwargs)

        return self.apply(self.values_column, diff, new_name)

    def plot2d(self, *args, **kwargs):
        """
        Plot this `HTable` with the argument column as X and values column as Y.
        Uses the same arguments as `matplotlib.pyplot.plot`.
        """

        assert (
            len(self.primary_key) == 1
        ), "plot2d is only valid with single argument tables"

        from matplotlib import pyplot as plt

        x: HColumn = self[self.primary_key[0]]
        y: HColumn = self[self.values_column]

        plt.xlabel(f"{x.name} ({x.unit})" if x.unit else x.name)
        plt.ylabel(f"{y.name} ({y.unit})" if y.unit else y.name)

        return plt.plot(x, y, *args, **kwargs)


def join_multiple(
    *tables,
    keys=None,
    join_type="inner",
    uniq_col_name="{col_name}_{table_name}",
    table_names=["1", "2"],
    metadata_conflicts="silent",
    join_funcs=None,
) -> Table:
    """
    `astropy.table.join` but with more than one table, iteratively from left to right.
    """

    _join = partial(
        join,
        keys=keys,
        join_type=join_type,
        uniq_col_name=uniq_col_name,
        table_names=table_names,
        metadata_conflicts=metadata_conflicts,
        join_funcs=join_funcs,
    )

    new_table = _join(*tables[:2])
    for t in tables[2:]:
        new_table = _join(new_table, t)

    return new_table

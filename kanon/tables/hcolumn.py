import importlib
from functools import wraps
from typing import Callable, Optional, Type, cast

import numpy as np
from astropy.table import Column
from astropy.table.column import ColumnInfo

from kanon.units import BasedReal
from kanon.units.precision import Truncable

__all__ = ["HColumn", "HColumnInfo"]


def _patch_dtype_info_name(func: Callable, col_arg: int):
    """
    Wrapper monkey patching `dtype_info_name` to replace it with a column `BasedReal`
    name if possible.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        col = args[col_arg]
        if col.basedtype:
            module = importlib.import_module(func.__module__)
            base_info_name = module.dtype_info_name
            module.dtype_info_name = lambda _: col.basedtype.__name__
            res = func(*args, **kwargs)
            module.dtype_info_name = base_info_name
            return res
        return func(*args, **kwargs)

    return wrapper


class HColumnInfo(ColumnInfo):
    """
    `~ColumnInfo` with `basedtype`
    """

    attrs_from_parent = ColumnInfo.attrs_from_parent | {"basedtype"}
    attr_names = ColumnInfo.attr_names | {"basedtype"}

    def new_like(self, cols, length, metadata_conflicts="warn", name=None):
        attrs = self.merge_cols_attributes(
            cols,
            metadata_conflicts,
            name,
            ("meta", "unit", "format", "basedtype", "description"),
        )

        return self._parent_cls(length=length, **attrs)


class HColumn(Column, Truncable):
    """
    `~astropy.table.Column` subclass with better support of `~kanon.units.radices.BasedReal`
    values.
    """

    info = HColumnInfo()

    _basedtype: Optional[Type[BasedReal]] = None

    def __new__(
        cls,
        data=None,
        name=None,
        dtype=None,
        shape=(),
        length=0,
        description=None,
        unit=None,
        format=None,
        meta=None,
        copy=False,
        copy_indices=True,
        basedtype: Optional[Type[BasedReal]] = None,
    ):

        if data is None and basedtype:
            data = np.zeros((length,) + shape, dtype="O")
            data = np.vectorize(basedtype.from_int)(data)

        self = super().__new__(
            cls,
            data=data,
            name=name,
            dtype=dtype,
            shape=shape,
            length=length,
            description=description,
            unit=unit,
            format=format,
            meta=meta,
            copy=copy,
            copy_indices=copy_indices,
        )

        if self.dtype == "object" and len(self) > 0:
            self._basedtype = type(self[0])
            assert all(isinstance(i, self.basedtype) for i in self)
        return self

    def __setitem__(self, index, value):
        array_value = np.array(value, ndmin=1)
        if self.basedtype and not all(
            isinstance(v, self.basedtype) for v in array_value
        ):
            raise ValueError(
                f"Value has not the same type {array_value.dtype} as this column {self.basedtype}"
            )
        return super().__setitem__(index, value)

    def _copy_attrs(self, obj):
        super()._copy_attrs(obj)
        if val := getattr(obj, "basedtype", None):
            self._basedtype = val

    @property
    def basedtype(self):
        return self._basedtype

    def astype(self, dtype, *args, **kwargs) -> "HColumn":
        res: "HColumn" = super().astype(dtype, *args, **kwargs)
        if np.dtype(dtype) != "O" and res.basedtype:
            res._basedtype = None

        elif np.dtype(dtype) == "O" and dtype is not self.basedtype:
            if isinstance(dtype, type) and issubclass(dtype, BasedReal):
                dtype = cast(Type[BasedReal], dtype)
                res._basedtype = dtype

                if self.basedtype:

                    def convert(x):
                        return dtype(x, self.significant)

                elif self.dtype == "int":
                    convert = dtype.from_int
                elif self.dtype == "float":

                    def convert(x):
                        return dtype.from_float(x, 3)

                else:
                    raise ValueError

                res.data[:] = np.vectorize(convert)(res.data)

        return res

    _base_repr_ = _patch_dtype_info_name(Column._base_repr_, 0)

    def truncate(self, significant: Optional[int] = None) -> "HColumn":
        return np.vectorize(lambda x: x.truncate(significant))(self)

    def ceil(self, significant: Optional[int] = None) -> "HColumn":
        return np.vectorize(lambda x: x.ceil(significant))(self)

    def floor(self, significant: Optional[int] = None) -> "HColumn":
        return np.vectorize(lambda x: x.floor(significant))(self)

    def __round__(self, significant: Optional[int] = None) -> "HColumn":
        return np.vectorize(lambda x: round(x, significant))(self)

    def resize(self, significant: int) -> "HColumn":
        return np.vectorize(lambda x: x.resize(significant))(self)

    @property
    def significant(self) -> Optional[int]:
        """
        If this column containes `BasedReal` values, return the minimum significant
        of all values. Else returns `None`
        """
        if self.basedtype:
            return min(x.significant for x in self)
        return None

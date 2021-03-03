from numbers import Number
from typing import Callable, TypeVar

import pandas as pd

__all__ = ["Interpolator", "linear_interpolation"]


NT = TypeVar("NT", bound=Number)

Interpolator = Callable[[pd.DataFrame, Number], NT]


def linear_interpolation(df: pd.DataFrame, key: Number) -> NT:
    """Linear interpolation
    """

    if df.index.dtype == 'object' and isinstance(key, float):
        key = type(df.index[0]).from_float(key, 4)

    try:
        low = df.truncate(after=key).iloc[-1]
        high = df.truncate(before=key).iloc[0]

        x = (low.name, low[0])
        y = (high.name, high[0])

    except IndexError:
        raise IndexError(f"Key ({key}) is out-of-bounds")

    return (y[1] - x[1]) * (key - x[0]) / (y[0] - x[0]) + x[1]

from numbers import Number
from typing import Callable, TypeVar

import pandas as pd

__all__ = ["Interpolator", "linear_interpolation"]


NT = TypeVar("NT", bound=Number)

Interpolator = Callable[[pd.DataFrame, Number], NT]


def linear_interpolation(df: pd.DataFrame, key: Number) -> NT:
    """Linear interpolation
    """
    try:
        key_as_float = float(key)
        low = df.truncate(after=key_as_float).iloc[-1]
        high = df.truncate(before=key_as_float).iloc[0]

        x = (low.name, low[0])
        y = (high.name, high[0])

    except IndexError:
        raise IndexError(f"Key ({key}) is out-of-bounds")

    return (y[1] - x[1]) * (key - x[0]) / (y[0] - x[0]) + x[1]

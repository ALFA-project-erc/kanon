from functools import wraps
from typing import Callable, Tuple

import pandas as pd
from scipy.interpolate import lagrange

from kanon.utils.types.number_types import Real

__all__ = ["Interpolator", "linear_interpolation"]


Interpolator = Callable[[pd.DataFrame, Real], Real]


def _split_df(df: pd.DataFrame, key: Real) -> Tuple[pd.DataFrame, pd.DataFrame]:

    df = df.rename_axis("x")
    df = df.rename(columns={list(df.columns)[0]: "y"})

    df = df.reset_index().set_index("x", drop=False)

    lower = df.truncate(after=key)
    upper = df.truncate(before=key)

    return lower, upper


def _interpolation_decorator(func):
    """
    This decorator automatically casts the key in the correct type and returns the result
    if the key is in the DataFrame
    """
    @wraps(func)
    def wrapper(df: pd.DataFrame, key: Real) -> Real:
        if df.index.dtype == 'object' and isinstance(key, float):
            key = type(df.index[0]).from_float(key, df.index[0].significant)
        if key in df.index:
            return df.loc[key][0]
        return func(df, key)

    return wrapper


@_interpolation_decorator
def linear_interpolation(df: pd.DataFrame, key: Real) -> Real:
    """Linear interpolation.
    Will prioritize taking the lower and upper value.
    The `pd.DataFrame` needs at least 2 rows.
    """

    assert len(df) >= 2, "The DataFrame needs at least 2 rows"

    lower, upper = _split_df(df, key)

    if len(lower) == 0:
        (_, a), (_, b) = upper.iloc[:2].T.iteritems()
    elif len(upper) == 0:
        (_, a), (_, b) = lower.iloc[-2:].T.iteritems()
    else:
        a = lower.iloc[-1]
        b = upper.iloc[0]

    c = (b.y - a.y) / (b.x - a.x)

    return c * (key - a.x) + a.y


@_interpolation_decorator
def quadratic_interpolation(df: pd.DataFrame, key: Real) -> Real:
    """Quadratic interpolation, from Lagrange
    Will prioritize taking 2 values before the keys and 1 after.
    The `pd.DataFrame` needs at least 2 rows.
    """

    assert len(df) >= 3, "The DataFrame needs at least 3 rows"

    lower, upper = _split_df(df, key)

    before = max(min(3 - min(len(upper), 1), len(lower)), 3 - len(upper))
    after = 3 - before

    values = pd.concat([lower.iloc[-before:], upper.iloc[:after]])

    poly = lagrange(list(values["x"]), list(values["y"]))

    return poly(key)

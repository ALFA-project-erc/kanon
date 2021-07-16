"""
Common interpolation methods are defined in this module.

There are 2 types of interpolation functions :

Single-Point Interpolators, which interpolate on a single value
    `linear_interpolation`

    `quadratic_interpolation`

Whole Interpolators, which interpolate on every `NaN` value
    `distributed_interpolation`
"""

from functools import wraps
from typing import Callable, Literal, Tuple

import numpy as np
import pandas as pd
from scipy.interpolate import lagrange

from kanon.utils.types.number_types import Real

__all__ = [
    "Interpolator",
    "linear_interpolation",
    "quadratic_interpolation",
    "distributed_interpolation",
]


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
        if df.index.dtype == "object" and isinstance(key, float):
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
    The `pd.DataFrame` needs at least 3 rows.
    """

    assert len(df) >= 3, "The DataFrame needs at least 3 rows"

    lower, upper = _split_df(df, key)

    before = max(min(3 - min(len(upper), 1), len(lower)), 3 - len(upper))
    after = 3 - before

    values = pd.concat([lower.iloc[-before:], upper.iloc[:after]])

    poly = lagrange(list(values["x"]), list(values["y"]))

    return poly(key)


# Whole DataFrame interpolation
# Interpolates on every NaN value


def distributed_interpolation(
    df: pd.DataFrame, direction: Literal["convex", "concave"]
):
    """Applies distributed interpolation on a `DataFrame` with a regularly stepped index.
    Interpolates on every unknown values (`numpy.nan` or `pandas.NA`).
    """

    df = df.copy()

    if direction not in ("convex", "concave"):
        raise ValueError(
            f"The interpolation direction must be either convex or concave, not {direction}"
        )

    if pd.isna(df.iloc[-1][0]) or pd.isna(df.iloc[0][0]):
        raise ValueError("The DataFrame must start and end with non nan values")

    if based_values := df.iloc[0].dtypes == "object":

        based_type = type(df.iloc[0][0])

        based_idx = df[~df.isna().any(axis=1)].index

        max_sig: int = df.loc[based_idx].applymap(lambda x: x.significant).max().iloc[0]
        df.loc[based_idx] = df.loc[based_idx].applymap(
            lambda x: x.subunit_quantity(max_sig)
        )

        df = df.astype(float)

    if df.isna().sum()[0] < len(df) - 2:

        def edges(x: pd.Series) -> float:
            if np.isnan(x).sum() == 1:
                return 1
            return np.nan

        bounds = df.rolling(2, 1).apply(edges).dropna().index

        for b in range(0, len(bounds), 2):
            lower = df.index.get_loc(bounds[b]) - 1
            upper = df.index.get_loc(bounds[b + 1]) + 1
            df.iloc[lower:upper] = distributed_interpolation(
                df.iloc[lower:upper], direction=direction
            )

    else:

        index_diff = df.index.to_series().diff().iloc[1:].to_numpy()
        step = index_diff[0]

        if not (index_diff == step).all():
            raise ValueError("The DataFrame must have regular steps")

        first: Real = df.iloc[0][0]
        last: Real = df.iloc[-1][0]

        q, r = divmod(last - first, len(df) - 1)

        r = r if direction == "concave" else r - len(df) + 2

        for idx, _ in df.iloc[1:-1].iterrows():
            first += q + (1 if r > 0 else 0)

            r += 1 if direction == "convex" else -1

            df.loc[idx] = first

    if based_values:
        df.loc[:] = df.applymap(lambda x: based_type.from_int(int(x)).shift(max_sig))

    return df

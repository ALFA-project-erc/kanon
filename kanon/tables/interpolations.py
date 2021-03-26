from functools import wraps
from typing import Callable, Literal, Tuple

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


# Whole DataFrame interpolation
# Interpolates on every NaN value

def distributed_interpolation(df: pd.DataFrame, direction: Literal["convex", "concave"]):
    """Applies distributed interpolation on a regular stepped indexed `DataFrame`.
    Interpolates every inner rows betweend the first and the last.
    """

    df = df.copy()

    index_diff = df.index.to_series().diff().iloc[1:].to_numpy()

    step = index_diff[0]

    if direction not in ("convex", "concave"):
        raise ValueError(f"The interpolation direction must be either convex or concave, not {direction}")

    if not (index_diff == step).all():
        raise ValueError("The DataFrame must have regular steps")

    if pd.isna(df.iloc[-1][0]) or pd.isna(df.iloc[0][0]):
        raise ValueError("The DataFrame must start and end with non nan values")

    lower: Tuple[Real, Real] = df.iloc[0][0]
    upper: Tuple[Real, Real] = df.iloc[-1][0]

    q, r = divmod(upper - lower, len(df) - 1)  # type: ignore

    r = r if direction == "concave" else r - len(df) + 2

    for idx, _ in df.iloc[1:-1].iterrows():
        lower += q + (1 if r > 0 else 0)

        r += 1 if direction == "convex" else -1

        df.loc[idx] = lower

    return df

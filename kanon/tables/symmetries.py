from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple

import pandas as pd
from pandas import DataFrame

from kanon.utils.types.number_types import Real

__all__ = ["Symmetry", "OutOfBoundsOriginError", "OverlappingSymmetryError"]


@dataclass
class Symmetry:
    """Defines a symmetry strategy that can be applied on a `~pandas.DataFrame`
    from a specified source interval to one or multiple target keys

    >>> df = DataFrame({"val": [5, 9, 2]} ,index=[0,1,3])
    >>> sym = Symmetry("mirror")
    >>> df.pipe(sym)
    val
    0   5
    1   9
    3   2
    5   9
    6   5
    >>> sym = Symmetry("periodic", sign=-1, offset=2)
    >>> df.pipe(sym)
    val
    0   5
    1   9
    3   2
    4  -3
    5  -7
    7   0
    >>> sym = Symmetry("periodic", sign=-1, source=(0,1), targets=[6,10])
    >>> df.pipe(sym)
    val
    0    5
    1    9
    3    2
    6   -5
    7   -9
    10  -5
    11  -9

    :param symtype: Type of the symmetry, it can be of the same direction (`periodic`) \
    or the oposite (`mirror`)
    :type symtype: Literal["periodic", "mirror"]
    :param offset: Offset to add to the symmetry values, defaults to 0
    :type offset: int, optional
    :param sign: Relative signs of the symmetry values from source values, defaults to 1
    :type sign: Literal[-1, 1], optional
    :param source: Tuple representing the lower and upper bound to take the values from, \
    defaults to the whole DataFrame
    :type source: Tuple[Real, Real], optional
    :param targets: List of keys where the symmetry are pasted, defaults to the end of \
    the DataFrame
    :type targets: List[int], optional
    """

    symtype: Literal["periodic", "mirror"]
    offset: int = 0
    sign: Literal[-1, 1] = 1
    source: Optional[Tuple[Real, Real]] = None
    targets: Optional[List[Real]] = None

    def __post_init__(self):
        if self.symtype not in ("periodic", "mirror"):
            raise ValueError
        if self.source:
            if self.source[0] >= self.source[1]:
                raise ValueError

    def __call__(self, df: DataFrame):

        if len(df) == 0:
            return df

        if self.source:
            if not (
                self.source[0] < df.index[-1] >= self.source[1]
                and self.source[0] >= df.index[0] < self.source[1]
            ):
                raise OutOfBoundsOriginError
            symdf = df.loc[self.source[0] : self.source[1]].copy()  # type: ignore
        else:
            symdf = df.copy()

        def apply(x):
            return self.sign * x + self.offset

        if not self.targets:

            if self.symtype == "mirror":
                symdf.index = symdf.index.map(lambda x: 2 * symdf.index[-1] - x)
                symdf = symdf[:-1][::-1]

            elif self.symtype == "periodic":
                symdf.index = symdf.index.map(
                    lambda x: 1 + x + symdf.index[-1] - symdf.index[0]
                )

            if self.sign == -1 or self.offset:
                symdf = symdf.applymap(apply)

            df = pd.concat([df, symdf])
        else:
            for t in self.targets:
                tdf = symdf.copy()

                if self.symtype == "mirror":
                    tdf.index = tdf.index.map(lambda x: tdf.index[-1] - x + t)
                    tdf = tdf[::-1]

                else:
                    tdf.index = tdf.index.map(lambda x: t + x - tdf.index[0])

                if self.sign == -1 or self.offset:
                    tdf = tdf.applymap(apply)

                if len(df.index.intersection(tdf.index)) > 0:
                    raise OverlappingSymmetryError

                df = pd.concat([df, tdf])

        return df.sort_index()


class OutOfBoundsOriginError(IndexError):
    """
    Catches applying on a DataFrame a symmetry with source values outside
    the DataFrame bounds
    """


class OverlappingSymmetryError(ValueError):
    """
    Catches applying on a DataFrame a symmetry with overlapping results
    """

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple

import pandas as pd
from pandas.core.frame import DataFrame

from histropy.utils.types.dishas import SymmetryType


@dataclass
class Symmetry:
    symtype: SymmetryType

    offset: int = 0
    sign: Literal[-1, 1] = 1
    anti: Literal[-1, 1] = 1
    origin: Optional[Tuple[int, int]] = None
    target: List[int] = field(default_factory=list)

    def __post_init__(self):
        if self.origin:
            if self.origin[0] >= self.origin[1]:
                raise ValueError

    def symmetric_df(self, df: DataFrame):

        if len(df) == 0:
            return df

        if self.origin:
            if not (self.origin[0] < df.index[-1] >= self.origin[1]
                    and self.origin[0] >= df.index[0] < self.origin[1]):
                raise OutOfBoundsOriginError
            symdf = df.loc[self.origin[0]:self.origin[1]].copy()
        else:
            symdf = df.copy()

        def apply(x):
            return self.sign * x + self.offset

        if not self.target:
            symdf.index = symdf.index.map(lambda x: 1 + x + symdf.index[-1] - symdf.index[0])

            if self.symtype == "mirror":
                symdf = symdf[:-1][::-1]

            if self.sign == -1 or self.offset:
                symdf = symdf.applymap(apply)

            df = pd.concat([df, symdf])

        for t in self.target:
            symdf.index = symdf.index.map(lambda x: t + x - symdf.index[0])

            if self.symtype == "mirror":
                symdf = symdf[::-1]

            if self.sign == -1 or self.offset:
                symdf = symdf.applymap(apply)

            if len(df.index.intersection(symdf.index)) > 0:
                raise OverlappingSymmetryError

            df = pd.concat([df, symdf])

        return df.applymap(lambda x: x * self.anti)


class OutOfBoundsOriginError(IndexError):
    """
    Catches applying on a DataFrame a symmetry with origin values outside
    the DataFrame bounds
    """
    pass


class OverlappingSymmetryError(ValueError):
    """
    Catches applying on a DataFrame a symmetry with overlapping results
    """
    pass

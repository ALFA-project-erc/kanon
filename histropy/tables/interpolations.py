from typing import Callable, Tuple

from histropy.utils.types_helper import NT

Interpolator = Callable[[Tuple[NT, NT], Tuple[NT, NT], NT], NT]


def linear_interpolation(x: Tuple[NT, NT], y: Tuple[NT, NT], t: NT) -> NT:
    return (y[1] - x[1]) * (t - x[0]) / (y[0] - x[0]) + x[1]

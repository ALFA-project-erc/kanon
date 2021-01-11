from typing import Tuple

from histropy.utils.types_helper import NT


def linear_interpolation(x: Tuple[NT, NT], y: Tuple[NT, NT], t: NT) -> NT:
    """Linear interpolation
    """
    return (y[1] - x[1]) * (t - x[0]) / (y[0] - x[0]) + x[1]

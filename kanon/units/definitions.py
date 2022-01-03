from .radices import BasedReal

__all__ = [
    "Sexagesimal",
    "Historical",
    "HistoricalDecimal",
    "IntegerAndSexagesimal",
    "Temporal",
]


class Sexagesimal(BasedReal, base=([60], [60])):
    pass


class Historical(BasedReal, base=([10, 12, 30], [60]), separators=["", "r ", "s "]):
    pass


class HistoricalDecimal(BasedReal, base=([10], [100])):
    pass


class IntegerAndSexagesimal(BasedReal, base=([10], [60])):
    pass


class Temporal(BasedReal, base=([10], [24, 60])):
    pass

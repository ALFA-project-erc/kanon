from .radices import BasedReal, RadixBase, radix_registry

__all__ = ["RadixBase", "BasedReal"]

# Load all common radices

Sexagesimal = radix_registry["Sexagesimal"]
Historical = radix_registry["Historical"]
HistoricalDecimal = radix_registry["HistoricalDecimal"]
IntegerAndSexagesimal = radix_registry["IntegerAndSexagesimal"]
Temporal = radix_registry["Temporal"]

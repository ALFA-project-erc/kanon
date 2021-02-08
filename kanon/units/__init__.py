from .radices import BasedReal, RadixBase, radix_registry

__all__ = ["RadixBase", "BasedReal"]

# Load all common radices
for name, br in radix_registry.items():
    locals()[name] = br
    __all__.append(name)

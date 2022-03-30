"""
>>> from kanon.tables import HTable
>>> table = HTable.read(193)
>>> table
<HTable length=60>
         Days                  Entries
          d                      deg
IntegerAndSexagesimal        Sexagesimal
--------------------- --------------------------
                 1 ;     59,08,19,37,19,13,56 ;
                 2 ;  01,58,16,39,14,38,27,52 ;
                 3 ;  02,57,24,58,51,57,41,48 ;
                  ...                        ...
                57 ;  56,10,54,38,27,16,14,12 ;
                58 ;  57,10,02,58,04,35,28,08 ;
                59 ;  58,09,11,17,41,54,42,04 ;
                60 ;  59,08,19,37,19,13,56,00 ;
>>> table.loc[2]["Entries"]
01,58,16,39,14,38,27,52 ;
"""

from astropy.io import registry

from .htable import HTable
from .htable_reader import read_table_dishas

__all__ = ["HTable"]


def dishas_identifier(_, *args, **kwargs):
    return isinstance(args[-1], int)


registry.register_identifier("dishas", HTable, dishas_identifier)
registry.register_reader("dishas", HTable, read_table_dishas)

:mod:`~kanon.tables` --- Defining ancient astronomical tables
=============================================================

.. py:module:: kanon.tables

>>> from kanon.tables import HTable
>>> table = HTable.read(193, format="dishas")
>>> table
<HTable length=60>
  Days           Entries
  d               deg
object           object
------ --------------------------
      1    59,08,19,37,19,13,56 ;
    ...                        ...
    59 58,09,11,17,41,54,42,04 ;
    60 59,08,19,37,19,13,56,00 ;
>>> table.loc[2]["Entries"]
01,58,16,39,14,38,27,52 ;


.. toctree::
  :maxdepth: 2

  htable.rst
  symmetries.rst
  interpolations.rst

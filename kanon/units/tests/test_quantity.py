import pytest
from astropy.units import Quantity
from astropy.units import arcminute as _arcminute
from astropy.units import degree as _degree
from astropy.units.core import Unit

from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity

degree: Unit = _degree
arcminute: Unit = _arcminute


class TestQuantity:
    def test_init_basedquantity(self):
        q = Sexagesimal(1) * degree
        assert isinstance(q, BasedQuantity)
        assert q.unit == degree
        assert q.value.equals(Sexagesimal(1))
        q = Sexagesimal(1) / degree
        assert isinstance(q, BasedQuantity)
        assert q.unit == 1 / degree
        assert q.value.equals(Sexagesimal(1))

        assert type(BasedQuantity(1, degree)) is Quantity

    def test_attribute_forwarding(self):
        q = Sexagesimal("1;0,1,31") * degree

        with pytest.raises(AttributeError):
            q._from_string()
        with pytest.raises(AttributeError):
            q.does_not_exist()

        assert q.truncate(2).value.equals(q.value.truncate(2))
        assert q.left == (1,)

        assert round(q, 2).value.equals(round(q.value, 2))

    @pytest.mark.filterwarnings("ignore")
    def test_shifting(self):
        q = Sexagesimal("1;0,1,31") * degree

        assert (q << 2).value.equals(q.value << 2)
        assert (q >> 2).value.equals(q.value >> 2)

        arcmq = q << 1 * arcminute
        assert arcmq.unit == arcminute
        assert arcmq.value.equals(Sexagesimal("1,0;1,31,0"))

        with pytest.raises(TypeError):
            q >> 1 * arcminute

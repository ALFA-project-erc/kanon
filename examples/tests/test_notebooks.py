from typing import Any, Dict

import pytest
from astropy.units import degree
from papermill.execute import execute_notebook

from kanon.units import Sexagesimal


class TestNotebooks:

    def get_nb(self, name: str, params: Dict[str, Any]):
        nb = execute_notebook(f'./examples/{name}.ipynb', "-", parameters=params)
        return nb

    @pytest.mark.parametrize("params,result", [
        ({"year": 1327, "month": 7, "day": 3}, "1,47;18,49"),
        ({"year": 1691, "month": 9, "day": 9}, "2,55;31,33"),
        ({"year": 998, "month": 10, "day": 2}, "03,13;25,33"),
        ({"year": 1998, "month": 2, "day": 10}, "05,34;29,06"),
    ])
    def test_sun_true_position(self, params, result):
        data = self.get_nb("sun_true_position", params).cells[-1].outputs[0].data["text/latex"]
        assert data == (Sexagesimal(result) * degree)._repr_latex_()

    @pytest.mark.parametrize("params,result", [
        ({"OBLIQUITY": "23;51,20"}, ("02;01,12,38", "23;51,20,22")),
        ({"OBLIQUITY": "0"}, ("0", "0")),
    ])
    def test_declination(self, params, result):
        data: str = self.get_nb("declination", params).cells[7].outputs[0].data["text/html"]
        lines = data.split("<tr>")
        line5 = [li for li in lines if "<td>05 ;" in li][0]
        line90 = [li for li in lines if "<td>01,30 ;" in li][0]
        assert repr(Sexagesimal(result[0])).strip() in line5
        assert repr(Sexagesimal(result[1])).strip() in line90

    @pytest.mark.parametrize("params,result", [
        ({"OBLIQUITY": "23;51,20"}, ("0.3111", "-3.0222")),
        ({"OBLIQUITY": "0"}, ("54610.2778", "55083.2889")),
    ])
    def test_ptolemy_viz(self, params, result):
        output = "".join(o["text"] for o in self.get_nb("ptolemy_viz", params).cells[9].outputs)
        assert f"mean : {result[0]}" in output
        assert f"mean : {result[1]}" in output

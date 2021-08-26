import glob
from typing import Any, Dict, List

import nbformat
import pytest
from astropy.units import degree
from nbformat import NotebookNode
from papermill.execute import execute_notebook

from kanon.units import Sexagesimal


def test_no_output():
    nbs: List[NotebookNode] = [
        nbformat.read(nb, nbformat.NO_CONVERT) for nb in glob.glob("./examples/*ipynb")
    ]
    for nb in nbs:
        for cell in nb.cells:
            assert "outputs" not in cell or len(cell.outputs) == 0


def get_nb(name: str, params: Dict[str, Any]) -> NotebookNode:
    nb = execute_notebook(f"./examples/{name}.ipynb", "-", parameters=params)
    return nb


@pytest.mark.parametrize(
    "params,result",
    [
        ({"year": 1327, "month": 7, "day": 3}, "1,47;18,48"),
        ({"year": 1691, "month": 9, "day": 9}, "2,55;31,33"),
        ({"year": 998, "month": 10, "day": 2}, "03,13;25,33"),
        ({"year": 1998, "month": 2, "day": 10}, "05,34;29,06"),
    ],
)
def test_sun_true_position(params, result):
    data = get_nb("sun_true_position", params).cells[-1].outputs[0].data["text/latex"]
    assert data == (Sexagesimal(result) * degree)._repr_latex_()


@pytest.mark.parametrize(
    "params,result",
    [
        ({"OBLIQUITY": "23;51,20"}, ("02;01,12,38", "23;51,20,22")),
        ({"OBLIQUITY": "0"}, ("0", "0")),
    ],
)
def test_declination(params, result):
    data: str = get_nb("declination", params).cells[7].outputs[0].data["text/html"]
    lines = data.split("<tr>")
    line5 = [li for li in lines if "<td>05 ;" in li][0]
    line90 = [li for li in lines if "<td>01,30 ;" in li][0]
    assert repr(Sexagesimal(result[0])).strip() in line5
    assert repr(Sexagesimal(result[1])).strip() in line90


@pytest.mark.parametrize(
    "params,result",
    [
        ({"OBLIQUITY": "23;51,20"}, ("0.3111", "-3.0222")),
        ({"OBLIQUITY": "0"}, ("54610.2778", "55083.2889")),
    ],
)
def test_ptolemy_viz(params, result):
    output = "".join(o["text"] for o in get_nb("ptolemy_viz", params).cells[9].outputs)
    assert f"mean : {result[0]}" in output
    assert f"mean : {result[1]}" in output

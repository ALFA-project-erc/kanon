import json

import pytest
import requests_mock as reqmock
from astropy.utils.data import get_pkg_data_filename


@pytest.fixture(autouse=True)
def mock_request_dishas(requests_mock: reqmock.Mocker):
    error = {"error": "Non existing id"}

    def callback(req, _):
        try:
            qid = req.query.split("&id=")[1].split("&source")[0]
            path = get_pkg_data_filename(f"data/table_content-{qid}.json")
            with open(path, "r") as f:
                content = json.load(f)
        except (OSError, IndexError):
            content = error
        return content

    requests_mock.get(reqmock.ANY, json=callback)

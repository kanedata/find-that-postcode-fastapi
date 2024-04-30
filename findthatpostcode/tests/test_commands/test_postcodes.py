import pytest
from click.testing import CliRunner

import findthatpostcode.utils
from findthatpostcode.commands.postcodes import (
    Postcode,
    db,
    import_nhspd,
    import_nspl,
    import_onspd,
    import_pcon,
)
from findthatpostcode.settings import NHSPD_URL, NSPL_URL, ONSPD_URL, PCON_URL
from findthatpostcode.tests.fixtures import MOCK_FILES, MockES, mock_bulk

files = [
    ("nspl", NSPL_URL, import_nspl),
    ("onspd", ONSPD_URL, import_onspd),
    ("nhspd", NHSPD_URL, import_nhspd),
    ("pcon", PCON_URL, import_pcon),
]

parameters = []
for f in files:
    url = f[1]
    parameters.append(tuple([*f, ["--file", MOCK_FILES[url]]]))
    parameters.append(tuple([*f, []]))
    parameters.append(tuple([*f, ["--url", url]]))


@pytest.mark.parametrize("filetype, url, command, args", parameters)
def test_import_postcode(filetype, url, command, args, requests_mock, monkeypatch):
    with open(
        MOCK_FILES[url],
        "rb",
    ) as f:
        requests_mock.get(url, content=f.read())
    monkeypatch.setattr(db, "get_db", lambda: MockES())
    monkeypatch.setattr(Postcode, "init", lambda *args, **kwargs: None)
    monkeypatch.setattr(findthatpostcode.utils, "bulk", mock_bulk)

    runner = CliRunner()

    result = runner.invoke(command, args, catch_exceptions=False)
    assert result.exit_code == 0

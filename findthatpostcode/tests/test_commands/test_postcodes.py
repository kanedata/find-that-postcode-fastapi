from click.testing import CliRunner

import findthatpostcode.utils
from findthatpostcode.commands.postcodes import Postcode, db, import_nspl
from findthatpostcode.settings import NSPL_URL
from findthatpostcode.tests.fixtures import MOCK_FILES, MockES, mock_bulk


def test_import_nspl(requests_mock, monkeypatch):
    with open(
        MOCK_FILES[NSPL_URL],
        "rb",
    ) as f:
        requests_mock.get(NSPL_URL, content=f.read())
    monkeypatch.setattr(db, "get_db", lambda: MockES())
    monkeypatch.setattr(Postcode, "init", lambda *args, **kwargs: None)
    monkeypatch.setattr(findthatpostcode.utils, "bulk", mock_bulk)

    runner = CliRunner()
    result = runner.invoke(import_nspl, catch_exceptions=False)
    assert result.exit_code == 0

    result = runner.invoke(
        import_nspl, ["--file", MOCK_FILES[NSPL_URL]], catch_exceptions=False
    )
    assert result.exit_code == 0

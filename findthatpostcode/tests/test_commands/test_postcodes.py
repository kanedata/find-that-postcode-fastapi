import os
import pytest
from click.testing import CliRunner
from findthatpostcode.commands.postcodes import import_nspl, db, Postcode
from findthatpostcode.settings import NSPL_URL
import findthatpostcode.utils
from findthatpostcode.tests.fixtures import mock_bulk, MockES, MOCK_FILES


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

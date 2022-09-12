import os

import pytest
from click.testing import CliRunner

import findthatpostcode.utils
from findthatpostcode.commands.codes import (
    Area,
    Entity,
    db,
    import_chd,
    import_msoa_names,
    import_rgc,
)
from findthatpostcode.settings import CHD_URL, MSOA_URL, RGC_URL
from findthatpostcode.tests.fixtures import MOCK_FILES, MockES, mock_bulk


@pytest.fixture
def mock_files(requests_mock, monkeypatch):
    for url, file_ in MOCK_FILES.items():
        with open(
            file_,
            "rb",
        ) as f:
            requests_mock.get(url, content=f.read())
    monkeypatch.setattr(db, "get_db", lambda: MockES())
    monkeypatch.setattr(Entity, "init", lambda *args, **kwargs: None)
    monkeypatch.setattr(Area, "init", lambda *args, **kwargs: None)
    monkeypatch.setattr(findthatpostcode.utils, "bulk", mock_bulk)


@pytest.mark.parametrize(
    "function,args",
    [
        (import_chd, []),
        (import_chd, ["--file", MOCK_FILES[CHD_URL]]),
        (import_rgc, []),
        (import_rgc, ["--file", MOCK_FILES[RGC_URL]]),
        (import_msoa_names, []),
        (import_msoa_names, ["--file", MOCK_FILES[MSOA_URL]]),
    ],
)
def test_import_codes(function, args, mock_files):

    runner = CliRunner()

    result = runner.invoke(function, args)
    assert result.exit_code == 0

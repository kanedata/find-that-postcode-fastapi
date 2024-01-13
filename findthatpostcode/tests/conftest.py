import pytest

import findthatpostcode.utils
from findthatpostcode.commands.codes import (
    Area,
    Entity,
    db,
)
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

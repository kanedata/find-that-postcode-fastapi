import datetime
import findthatpostcode.utils
from findthatpostcode.utils import (
    process_date,
    process_int,
    process_float,
    BulkImporter,
)
from findthatpostcode.tests.fixtures import mock_bulk
import pytest


@pytest.mark.parametrize(
    "value, expected, kwargs",
    [
        ("", None, {}),
        ("n/a", None, {}),
        (None, None, {}),
        ("01/01/2020", datetime.datetime(2020, 1, 1, 0, 0), {}),
        (
            "01/01/2020 12:00",
            datetime.datetime(2020, 1, 1, 12, 0),
            {"date_format": "%d/%m/%Y %H:%M"},
        ),
        (
            "2020-01-01 12:00:00",
            datetime.datetime(2020, 1, 1, 12, 0),
            {"date_format": "%Y-%m-%d %H:%M:%S"},
        ),
        (
            "2020-01-01",
            datetime.datetime(2020, 1, 1, 0, 0),
            {"date_format": "%Y-%m-%d"},
        ),
    ],
)
def test_process_date(value, expected, kwargs):
    assert process_date(value, **kwargs) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", None),
        ("n/a", None),
        (None, None),
        (datetime.date(2020, 1, 1), datetime.date(2020, 1, 1)),
        (4, 4),
        (4000, 4000),
        ("4,000", 4000),
        ("4000", 4000),
    ],
)
def test_process_int(value, expected):
    assert process_int(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", None),
        ("n/a", None),
        (None, None),
        (datetime.date(2020, 1, 1), datetime.date(2020, 1, 1)),
        (4, 4),
        (4000, 4000),
        ("4,000", 4000),
        ("4000", 4000),
        ("4000.0001", 4000.0001),
        ("4000.8", 4000.8),
        ("4,000.0001", 4000.0001),
        ("4,000.8", 4000.8),
    ],
)
def test_process_float(value, expected):
    assert process_float(value) == expected


def test_bulk_importer(monkeypatch):
    monkeypatch.setattr(findthatpostcode.utils, "bulk", mock_bulk)

    with BulkImporter(None, name="test", limit=3) as bulk_importer:
        for i in range(10):
            bulk_importer.add({"_index": "test", "_id": i, "_source": {"id": i}})
            assert len(bulk_importer) == (i + 1) % 3
        assert len(bulk_importer.errors) == 0

    with BulkImporter(None, name="test", limit=3) as bulk_importer:
        for i in range(10):
            bulk_importer.append({"_index": "test", "_id": i, "_source": {"id": i}})
            assert len(bulk_importer) == (i + 1) % 3
        assert len(bulk_importer.errors) == 0

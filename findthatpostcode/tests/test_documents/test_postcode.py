from findthatpostcode.documents import Postcode
import pytest


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", None),
        (None, None),
        ("   ", None),
        ("AB1 1AB", "AB1 1AB"),
        ("AB1   1AB", "AB1 1AB"),
        ("AB1 @$% 1AB", "AB1 1AB"),
        ("ab1 1Ab", "AB1 1AB"),
        ("AB1 OAB", "AB1 0AB"),
        ("AB1A 1AB", "AB1A 1AB"),
        ("AB1A 1ABGB", "AB1A1ABGB"),
    ],
)
def test_parse_id(value, expected):
    assert Postcode.parse_id(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", None),
        (None, None),
        ("   ", None),
        ("AB1 1AB", ("AB", "AB1", "AB1 1")),
        ("AB1   1AB", ("AB", "AB1", "AB1 1")),
        ("AB1 @$% 1AB", ("AB", "AB1", "AB1 1")),
        ("ab1 1Ab", ("AB", "AB1", "AB1 1")),
        ("AB1 OAB", ("AB", "AB1", "AB1 0")),
        ("AB1A 1AB", ("AB", "AB1A", "AB1A 1")),
        # ("AB1A 1ABGB", ("AB", "AB1A", "AB1A 1")),
    ],
)
def test_split_postcode(value, expected):
    assert Postcode.split_postcode(value) == expected

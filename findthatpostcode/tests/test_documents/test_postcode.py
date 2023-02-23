from typing import Optional, Tuple

import pytest

from findthatpostcode.documents import Postcode
from findthatpostcode.utils import PostcodeStr


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", ValueError),
        (None, ValueError),
        ("   ", ValueError),
        ("AB1 1AB", "AB1 1AB"),
        ("AB1   1AB", "AB1 1AB"),
        ("AB1 @$% 1AB", "AB1 1AB"),
        ("ab1 1Ab", "AB1 1AB"),
        ("AB1 OAB", "AB1 0AB"),
        ("AB1A 1AB", "AB1A 1AB"),
        ("AB1A 1ABGB", ValueError),
    ],
)
def test_parse_id(value, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            PostcodeStr(value)
        return
    assert PostcodeStr(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", ValueError),
        (None, ValueError),
        ("   ", ValueError),
        ("AB1 1AB", ("AB", "AB1", "AB1 1")),
        ("AB1   1AB", ("AB", "AB1", "AB1 1")),
        ("AB1 @$% 1AB", ("AB", "AB1", "AB1 1")),
        ("ab1 1Ab", ("AB", "AB1", "AB1 1")),
        ("AB1 OAB", ("AB", "AB1", "AB1 0")),
        ("AB1A 1AB", ("AB", "AB1A", "AB1A 1")),
        # ("AB1A 1ABGB", ("AB", "AB1A", "AB1A 1")),
    ],
)
def test_split_postcode(value: str, expected: Tuple[str, str, str]):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            PostcodeStr(value)
        return
    postcode_value = PostcodeStr(value)
    assert postcode_value.postcode_area == expected[0]
    assert postcode_value.postcode_district == expected[1]
    assert postcode_value.postcode_sector == expected[2]

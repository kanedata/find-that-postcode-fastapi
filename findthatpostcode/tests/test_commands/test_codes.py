import pytest
from click.testing import CliRunner

from findthatpostcode.commands.codes import (
    import_chd,
    import_msoa_names,
    import_rgc,
)
from findthatpostcode.settings import CHD_URL, MSOA_URL, RGC_URL
from findthatpostcode.tests.fixtures import MOCK_FILES


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

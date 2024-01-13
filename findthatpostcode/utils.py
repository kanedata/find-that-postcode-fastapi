import datetime
import re
from itertools import takewhile
from typing import Any, Dict, Optional

from elasticsearch.helpers import bulk

LATLONG_REGEX = re.compile(r"^(?P<lat>\-?\d+\.[0-9]+),(?P<lon>\-?\d+\.\d+)$")
POSTCODE_REGEX = re.compile(r"^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$")
POSTCODE_REGEX = re.compile(
    r"^(([A-Z]{1,2}[0-9][A-Z0-9]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA) ?[0-9][A-Z]{2}|BFPO ?[0-9]{1,4}|(KY[0-9]|MSR|VG|AI)[ -]?[0-9]{4}|[A-Z]{2} ?[0-9]{2}|GE ?CX|GIR ?0A{2}|SAN ?TA1)$"
)

POSTCODE_AREAS = {
    "AB": "Aberdeen",
    "AL": "St Albans",
    "B": "Birmingham",
    "BA": "Bath",
    "BB": "Blackburn",
    "BD": "Bradford",
    "BH": "Bournemouth",
    "BL": "Bolton",
    "BN": "Brighton",
    "BR": "Bromley",
    "BS": "Bristol",
    "BT": "Belfast",
    "CA": "Carlisle",
    "CB": "Cambridge",
    "CF": "Cardiff",
    "CH": "Chester",
    "CM": "Chelmsford",
    "CO": "Colchester",
    "CR": "Croydon",
    "CT": "Canterbury",
    "CV": "Coventry",
    "CW": "Crewe",
    "DA": "Dartford",
    "DD": "Dundee",
    "DE": "Derby",
    "DG": "Dumfries",
    "DH": "Durham",
    "DL": "Darlington",
    "DN": "Doncaster",
    "DT": "Dorchester",
    "DY": "Dudley",
    "E": "East London",
    "EC": "East Central London",
    "EH": "Edinburgh",
    "EN": "Enfield",
    "EX": "Exeter",
    "FK": "Falkirk",
    "FY": "Blackpool",
    "G": "Glasgow",
    "GL": "Gloucester",
    "GU": "Guildford",
    "HA": "Harrow",
    "HD": "Huddersfield",
    "HG": "Harrogate",
    "HP": "Hemel Hempstead",
    "HR": "Hereford",
    "HS": "Hebrides",
    "HU": "Hull",
    "HX": "Halifax",
    "IG": "Ilford",
    "IP": "Ipswich",
    "IV": "Inverness",
    "KA": "Kilmarnock",
    "KT": "Kingston upon Thames",
    "KW": "Kirkwall",
    "KY": "Kirkcaldy",
    "L": "Liverpool",
    "LA": "Lancaster",
    "LD": "Llandrindod Wells",
    "LE": "Leicester",
    "LL": "Llandudno",
    "LN": "Lincoln",
    "LS": "Leeds",
    "LU": "Luton",
    "M": "Manchester",
    "ME": "Medway",
    "MK": "Milton Keynes",
    "ML": "Motherwell",
    "N": "North London",
    "NE": "Newcastle upon Tyne",
    "NG": "Nottingham",
    "NN": "Northampton",
    "NP": "Newport",
    "NR": "Norwich",
    "NW": "North West London",
    "OL": "Oldham",
    "OX": "Oxford",
    "PA": "Paisley",
    "PE": "Peterborough",
    "PH": "Perth",
    "PL": "Plymouth",
    "PO": "Portsmouth",
    "PR": "Preston",
    "RG": "Reading",
    "RH": "Redhill",
    "RM": "Romford",
    "S": "Sheffield",
    "SA": "Swansea",
    "SE": "South East London",
    "SG": "Stevenage",
    "SK": "Stockport",
    "SL": "Slough",
    "SM": "Sutton",
    "SN": "Swindon",
    "SO": "Southampton",
    "SP": "Salisbury",
    "SR": "Sunderland",
    "SS": "Southend-on-Sea",
    "ST": "Stoke-on-Trent",
    "SW": "South West London",
    "SY": "Shrewsbury",
    "TA": "Taunton",
    "TD": "Galashiels",
    "TF": "Telford",
    "TN": "Tunbridge Wells",
    "TQ": "Torquay",
    "TR": "Truro",
    "TS": "Teesside",
    "TW": "Twickenham",
    "UB": "Southall",
    "W": "West London",
    "WA": "Warrington",
    "WC": "West Central London",
    "WD": "Watford",
    "WF": "Wakefield",
    "WN": "Wigan",
    "WR": "Worcester",
    "WS": "Walsall",
    "WV": "Wolverhampton",
    "YO": "York",
    "ZE": "Lerwick",
    "GY": "Guernsey",
    "JE": "Jersey",
    "IM": "Isle of Man",
    "GIR": "Girobank",
    "BFPO": "British Forces Post Office",
    "BF": "British Forces",
    "ASCN": "Ascension Island",
    "BIQQ": "British Antarctic Territory",
    "PCRN": "Pitcairn Islands",
    "STHL": "Saint Helena",
    "TDCU": "Tristan da Cunha",
    "TKCA": "Turks and Caicos Islands",
    "XX": "Online Only",
    "BX": "Non-geographic",
    "XM": "Christmas",
}


class BulkImporter:
    def __init__(self, es, name="records", limit=10000, **kwargs):
        self.es = es
        self.name = name
        self.limit = limit
        self._bulk_kwargs = kwargs
        self._records = []
        self.errors = []
        self.error_count = 0
        self._total_records = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    def __len__(self) -> int:
        return len(self._records)

    def add(self, record) -> None:
        self._records.append(record)
        self._total_records += 1
        if self.limit and (len(self._records) >= self.limit):
            self.commit()

    def append(self, *args, **kwargs) -> None:
        self.add(*args, **kwargs)

    def commit(self) -> None:
        print(f"[elasticsearch] Processed {self._total_records:,.0f} {self.name}")
        print(f"[elasticsearch] {len(self._records):,.0f} {self.name} to save")
        success, errors = bulk(self.es, self._records, **self._bulk_kwargs)
        error_count = errors if isinstance(errors, int) else len(errors)
        print(f"[elasticsearch] saved {success:,.0f} {self.name}")
        print(f"[elasticsearch] {error_count:,.0f} errors reported")
        if isinstance(errors, list):
            self.errors.extend(errors)
        self.error_count += error_count
        self._records = []


def process_date(
    value: Optional[str], date_format: str = "%d/%m/%Y"
) -> Optional[datetime.datetime]:
    if value is None or value in ["", "n/a"]:
        return None
    return datetime.datetime.strptime(value, date_format)


def process_int(value: Optional[str]) -> Optional[int]:
    if value is None or value in ["", "n/a"]:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return int(value)


def process_float(value: Optional[str]) -> Optional[float]:
    if value is None or value in ["", "n/a"]:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return float(value)


def is_latlon(q: str) -> Dict[str, float] | bool:
    q = q.strip().replace(" ", "")
    m = LATLONG_REGEX.match(q)
    if m:
        return {
            "lat": float(m.group("lat")),
            "lon": float(m.group("lon")),
        }
    return False


def is_postcode(q):
    q = q.strip().replace(" ", "").upper()
    return bool(POSTCODE_REGEX.match(q))


class PostcodeStr:
    def __init__(self, postcode: str, *args, **kwargs):
        if postcode is None:
            raise ValueError(f"Invalid postcode {postcode}")

        self._outward_code: str = ""
        self._inward_code: str = ""
        self.postcode: str = ""

        # check for blank/empty
        # put in all caps
        postcode = postcode.strip().upper()
        if postcode == "":
            raise ValueError(f"Invalid postcode {postcode}")

        # replace any non alphanumeric characters
        postcode = re.sub(r"[^0-9a-zA-Z]+", "", postcode)

        # check for nonstandard codes
        if len(postcode) > 7:
            raise ValueError(f"Invalid postcode {postcode}")

        first_part = postcode[:-3].strip()
        last_part = postcode[-3:].strip()

        # check for incorrect characters
        first_part = list(first_part)
        last_part = list(last_part)
        if last_part[0] == "O":
            last_part[0] = "0"

        self._outward_code = "".join(first_part).strip().upper()
        self._inward_code = "".join(last_part).strip().upper()

        self.postcode = "{} {}".format(self._outward_code, self._inward_code)

        s = self.postcode.replace(" ", "")
        validates = bool(POSTCODE_REGEX.match(s))
        if not validates:
            raise ValueError(f"Invalid postcode {s}")

    def __str__(self):
        return self.postcode

    def __repr__(self):
        return self.postcode

    def __eq__(self, other):
        return str(self) == other

    def __getattr__(self, __name: str) -> Any:
        if hasattr(self.postcode, __name):
            return getattr(self.postcode, __name)

    @property
    def postcode_area(self) -> str:
        """
        Get the postcode area for a postcode

        >>> PostcodeStr("SW1A 1AA").postcode_area
        'SW'
        """
        return "".join(takewhile(lambda x: x.isalpha(), self._outward_code))

    @property
    def postcode_district(self) -> str:
        """
        Get the postcode district for a postcode

        >>> PostcodeStr("SW1A 1AA").postcode_district
        'SW1A'
        """
        return self._outward_code

    @property
    def postcode_sector(self) -> str:
        """
        Get the postcode sector for a postcode

        >>> PostcodeStr("SW1A 1AA").postcode_sector
        'SW1A 1'
        """
        return self.postcode[:-2]

import datetime
import re

from elasticsearch.helpers import bulk

LATLONG_REGEX = re.compile(r"^(?P<lat>\-?\d+\.[0-9]+),(?P<lon>\-?\d+\.\d+)$")
POSTCODE_REGEX = re.compile(r"^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$")


class BulkImporter:
    def __init__(self, es, name="records", limit=10000, **kwargs):
        self.es = es
        self.name = name
        self.limit = limit
        self._bulk_kwargs = kwargs
        self._records = []
        self.errors = []
        self._total_records = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    def __len__(self):
        return len(self._records)

    def add(self, record):
        self._records.append(record)
        self._total_records += 1
        if self.limit and (len(self._records) >= self.limit):
            self.commit()

    def append(self, *args, **kwargs):
        self.add(*args, **kwargs)

    def commit(self):
        print(f"[elasticsearch] Processed {self._total_records:,.0f} {self.name}")
        print(f"[elasticsearch] {len(self._records):,.0f} {self.name} to save")
        success, errors = bulk(self.es, self._records, **self._bulk_kwargs)
        print(f"[elasticsearch] saved {success:,.0f} {self.name}")
        print(f"[elasticsearch] {len(errors):,.0f} errors reported")
        self.errors.extend(errors)
        self._records = []


def process_date(value, date_format="%d/%m/%Y"):
    if value in ["", "n/a", None]:
        return None
    return datetime.datetime.strptime(value, date_format)


def process_int(value):
    if value in ["", "n/a", None]:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return int(value)


def process_float(value):
    if value in ["", "n/a", None]:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return float(value)


def is_latlon(q):
    q = q.strip().replace(" ", "")
    m = LATLONG_REGEX.match(q)
    if m:
        return {
            "lat": m.group("lat"),
            "lon": m.group("lon"),
        }
    return False


def is_postcode(q):
    q = q.strip().replace(" ", "").upper()
    return bool(POSTCODE_REGEX.match(q))

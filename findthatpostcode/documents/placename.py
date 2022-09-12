import datetime
import hashlib
import re
from itertools import takewhile

from elasticsearch_dsl import Document, field

from findthatpostcode import settings
from findthatpostcode.utils import process_date, process_int


class Placename(Document):
    place18cd = field.Keyword()
    place18nm = field.Text()
    splitind = field.Boolean()
    descnm = field.Keyword()
    ctyhistnam = field.Keyword()
    ctyltnm = field.Keyword()
    cty = field.Keyword()
    laua = field.Keyword()
    ward = field.Keyword()
    parish = field.Keyword()
    hlth = field.Keyword()
    rgd = field.Keyword()
    rgn = field.Keyword()
    park = field.Keyword()
    bua11 = field.Keyword()
    pcon = field.Keyword()
    eer = field.Keyword()
    pfa = field.Keyword()
    cty = field.Keyword()
    laua = field.Keyword()
    ward = field.Keyword()
    parish = field.Keyword()
    hlth = field.Keyword()
    rgd = field.Keyword()
    rgn = field.Keyword()
    park = field.Keyword()
    bua11 = field.Keyword()
    pcon = field.Keyword()
    eer = field.Keyword()
    pfa = field.Keyword()
    gridgb1m = field.Keyword()
    gridgb1e = field.Integer()
    gridgb1n = field.Integer()
    grid1km = field.Keyword()
    lat = field.Float()
    long = field.Float()

    # added fields
    location = field.GeoPoint()
    alternative_names = field.Text()

    class Index:
        name = settings.ES_INDICES["placename"]

    @classmethod
    def from_csv(cls, record):

        # clean the record
        record = {
            k: None if v.strip() in ["", "n/a"] else v.strip()
            for k, v in record.items()
        }

        # tidy up a couple of records
        record["Related entity codes"] = (
            [v.strip() for v in record["Related entity codes"].split(",")]
            if record["Related entity codes"]
            else []
        )

        return cls(
            **{
                "code": record["Entity code"],
                "name": record["Entity name"],
                "abbreviation": record["Entity abbreviation"],
                "theme": record["Entity theme"],
                "coverage": record["Entity coverage"],
                "related_codes": record["Related entity codes"],
                "status": record["Status"],
                "live_instances": process_int(record["Number of live instances"]),
                "archived_instances": process_int(
                    record["Number of archived instances"]
                ),
                "crossborder_instances": process_int(
                    record["Number of cross-border instances"]
                ),
                "last_modified": process_date(record["Date of last instance change"]),
                "current_code_first": record["Current code (first in range)"],
                "current_code_last": record["Current code (last in range)"],
                "reserved_code": record["Reserved code (for CHD use)"],
                "owner": record.get("Entity owner"),
                "date_introduced": process_date(
                    record["Date entity introduced on RGC"]
                ),
                "date_start": process_date(record["Entity start date"]),
                "type": settings.ENTITIES.get(record["Entity code"]),
            }
        )

import datetime
import hashlib
import re
from itertools import takewhile

from elasticsearch_dsl import Document, field

from findthatpostcode import settings
from findthatpostcode.utils import process_date, process_int


class Entity(Document):
    code = field.Keyword()
    name = field.Text()
    abbreviation = field.Keyword()
    theme = field.Keyword()
    coverage = field.Keyword()
    related_codes = field.Keyword()
    status = field.Keyword()
    live_instances = field.Integer()
    archived_instances = field.Integer()
    crossborder_instances = field.Integer()
    last_modified = field.Date()
    current_code_first = field.Keyword()
    current_code_last = field.Keyword()
    reserved_code = field.Keyword()
    owner = field.Keyword()
    date_introduced = field.Date()
    date_start = field.Date()
    type = field.Keyword()

    class Index:
        name = settings.ES_INDICES["areatype"]

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

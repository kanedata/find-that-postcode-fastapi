import datetime
import hashlib
from typing import Any, Dict, List

from elasticsearch_dsl import Document, field

from findthatpostcode import settings
from findthatpostcode.utils import PostcodeStr


class Postcode(Document):
    pcd = field.Keyword()
    pcd2 = field.Keyword()
    pcds = field.Keyword()
    dointr = field.Date()
    doterm = field.Date()
    usertype = field.Integer()
    oseast1m = field.Integer()
    osnrth1m = field.Integer()
    osgrdind = field.Integer()
    oa21 = field.Keyword()
    oa11 = field.Keyword()
    cty = field.Keyword()
    ced = field.Keyword()
    laua = field.Keyword()
    ward = field.Keyword()
    hlthau = field.Keyword()
    nhser = field.Keyword()
    ctry = field.Keyword()
    rgn = field.Keyword()
    pcon = field.Keyword()
    eer = field.Keyword()
    teclec = field.Keyword()
    ttwa = field.Keyword()
    pct = field.Keyword()
    itl = field.Keyword()
    npark = field.Keyword()
    lsoa21 = field.Keyword()
    lsoa11 = field.Keyword()
    msoa21 = field.Keyword()
    msoa11 = field.Keyword()
    wz11 = field.Keyword()
    ccg = field.Keyword()
    bua11 = field.Keyword()
    buasd11 = field.Keyword()
    ru11ind = field.Keyword()
    oac11 = field.Keyword()
    lat = field.Float()
    long = field.Float()
    lep1 = field.Keyword()
    lep2 = field.Keyword()
    pfa = field.Keyword()
    imd = field.Integer()
    calncv = field.Keyword()
    stp = field.Keyword()

    # added fields
    location = field.GeoPoint()
    hash = field.Text(index_prefixes={})
    postcode_area = field.Keyword()
    postcode_district = field.Keyword()
    postcode_sector = field.Keyword()

    class Index:
        name = settings.ES_INDICES["postcode"]

    def area_codes(self) -> List[str]:
        return [f for f in self.to_dict().values() if isinstance(f, str)]

    @classmethod
    def from_csv(cls, original_record: Dict[str, str]) -> "Postcode":
        """Create a Postcode object from a NSPL record"""
        record: Dict[str, Any] = original_record.copy()
        postcode = PostcodeStr(record["pcds"])

        # null any blank fields (or ones with a dummy code in)
        for k in record:
            if record[k] == "" or record[k].endswith("99999999"):
                record[k] = None

        # date fields
        for date_field in ["dointr", "doterm"]:
            if record[date_field]:
                record[date_field] = datetime.datetime.strptime(
                    record[date_field], "%Y%m"
                )

        # latitude and longitude
        for geo_field in ["lat", "long"]:
            if record[geo_field]:
                record[geo_field] = float(record[geo_field])
                if record[geo_field] == 99.999999:
                    record[geo_field] = None
        if record["lat"] and record["long"]:
            record["location"] = {"lat": record["lat"], "lon": record["long"]}

        # integer fields
        for int_field in ["oseast1m", "osnrth1m", "usertype", "osgrdind", "imd"]:
            if record[int_field]:
                record[int_field] = int(record[int_field])

        # add postcode hash
        record["hash"] = hashlib.md5(
            postcode.lower().replace(" ", "").encode()
        ).hexdigest()

        # add postcode
        record["postcode_area"] = postcode.postcode_area
        record["postcode_district"] = postcode.postcode_district
        record["postcode_sector"] = postcode.postcode_sector

        p = cls(**record)
        p.meta["id"] = postcode
        return p

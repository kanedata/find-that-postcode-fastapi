import datetime
import hashlib
import re
from itertools import takewhile

from elasticsearch_dsl import Document, field

from findthatpostcode import settings


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

    def area_codes(self):
        return [f for f in self.to_dict().values() if isinstance(f, str)]

    @classmethod
    def from_csv(cls, record):
        """Create a Postcode object from a NSPL record"""
        # null any blank fields (or ones with a dummy code in)
        for k in record:
            if record[k] == "" or record[k].endswith("99999999"):
                record[k] = None

        # date fields
        for field in ["dointr", "doterm"]:
            if record[field]:
                record[field] = datetime.datetime.strptime(record[field], "%Y%m")

        # latitude and longitude
        for field in ["lat", "long"]:
            if record[field]:
                record[field] = float(record[field])
                if record[field] == 99.999999:
                    record[field] = None
        if record["lat"] and record["long"]:
            record["location"] = {"lat": record["lat"], "lon": record["long"]}

        # integer fields
        for j in ["oseast1m", "osnrth1m", "usertype", "osgrdind", "imd"]:
            if record[field]:
                record[field] = int(record[field])

        # add postcode hash
        record["hash"] = hashlib.md5(
            record["pcds"].lower().replace(" ", "").encode()
        ).hexdigest()

        # add postcode
        (
            postcode_area,
            postcode_district,
            postcode_sector,
        ) = Postcode.split_postcode(record["pcds"])
        record["postcode_area"] = postcode_area
        record["postcode_district"] = postcode_district
        record["postcode_sector"] = postcode_sector

        p = cls(**record)
        p.meta.id = record["pcds"]
        return p

    @staticmethod
    def parse_id(postcode):
        """
        standardises a postcode into the correct format
        """

        if postcode is None:
            return None

        # check for blank/empty
        # put in all caps
        postcode = postcode.strip().upper()
        if postcode == "":
            return None

        # replace any non alphanumeric characters
        postcode = re.sub("[^0-9a-zA-Z]+", "", postcode)

        # check for nonstandard codes
        if len(postcode) > 7:
            return postcode

        first_part = postcode[:-3].strip()
        last_part = postcode[-3:].strip()

        # check for incorrect characters
        first_part = list(first_part)
        last_part = list(last_part)
        if last_part[0] == "O":
            last_part[0] = "0"

        return "%s %s" % ("".join(first_part), "".join(last_part))

    @staticmethod
    def split_postcode(postcode):
        """
        splits a postcode into its component parts
        """

        if postcode is None:
            return None

        postcode = Postcode.parse_id(postcode)
        if postcode is None:
            return None

        postcode_first, _ = postcode.split()
        postcode_area = "".join(takewhile(lambda x: x.isalpha(), postcode_first))
        postcode_district = postcode_first
        postcode_sector = postcode[:-2]

        return postcode_area, postcode_district, postcode_sector

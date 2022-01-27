import re

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String

from findthatpostcode.database import Base, UpdatingTable


class Postcode(UpdatingTable, Base):
    __tablename__ = "postcodes"
    id = Column(Integer, primary_key=True)
    pcd = Column(String(7), unique=True, index=True)
    pcd2 = Column(String(8), unique=True, index=True)
    pcds = Column(String(8), unique=True, index=True)
    dointr = Column(Date())
    doterm = Column(Date())
    usertype = Column(Integer())
    oseast1m = Column(Integer())
    osnrth1m = Column(Integer())
    osnrth1m = Column(Integer())
    osgrdind = Column(Integer())
    oa11 = Column(String(9))
    cty = Column(String(9))
    ced = Column(String(9))
    laua = Column(String(9))
    ward = Column(String(9))
    hlthau = Column(String(9))
    nhser = Column(String(9))
    ctry = Column(String(9))
    rgn = Column(String(9))
    pcon = Column(String(9))
    eer = Column(String(9))
    teclec = Column(String(9))
    ttwa = Column(String(9))
    pct = Column(String(9))
    nuts = Column(String(9))
    npark = Column(String(9))
    lsoa11 = Column(String(9))
    msoa11 = Column(String(9))
    wz11 = Column(String(9))
    ccg = Column(String(9))
    bua11 = Column(String(9))
    buasd11 = Column(String(9))
    ru11ind = Column(String(2))
    oac11 = Column(String(3))
    lat = Column(Float())
    long = Column(Float())
    lep1 = Column(String(9))
    lep2 = Column(String(9))
    pfa = Column(String(9))
    imd = Column(Integer())
    calncv = Column(String(9))
    stp = Column(String(9))
    hash = Column(String(32), index=True)
    geom = Column(Geometry("POINT", srid=4326))

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

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

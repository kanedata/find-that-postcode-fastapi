import datetime
import hashlib
from itertools import takewhile
import re
from elasticsearch_dsl import (
    Document,
    InnerDoc,
    field,
)
from findthatpostcode import settings


class AreaEquivalents(InnerDoc):
    ons = field.Keyword()
    mhclg = field.Keyword()
    nhs = field.Keyword()
    scottish_government = field.Keyword()
    welsh_government = field.Keyword()


class Area(Document):
    code = field.Keyword()
    name = field.Text()
    name_welsh = field.Text()
    statutory_instrument_id = field.Keyword()
    statutory_instrument_title = field.Text()
    date_start = field.Date()
    date_end = field.Date()
    parent = field.Keyword()
    entity = field.Keyword()
    owner = field.Keyword()
    active = field.Keyword()
    areaehect = field.Float()
    areachect = field.Float()
    areaihect = field.Float()
    arealhect = field.Float()
    sort_order = field.Keyword()
    predecessor = field.Keyword()
    successor = field.Keyword()
    equivalents = field.Nested(AreaEquivalents)
    type = field.Keyword()
    alternative_names = field.Text()
    boundary = field.GeoShape()

    class Index:
        name = settings.ES_INDICES["area"]

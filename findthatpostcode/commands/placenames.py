"""
Import commands for placenames
"""
import csv
import io
import zipfile
from collections import defaultdict

import click
import requests
import requests_cache

from findthatpostcode import db, settings
from findthatpostcode.documents import Placename
from findthatpostcode.utils import BulkImporter

PLACENAMES_INDEX = Placename.Index.name


PLACE_TYPES = {
    "BUA": ["Built-up Area", "England and Wales"],
    "BUASD": ["Built-up Area Sub-Division", "England and Wales"],
    "CA": ["Council Area", "Scotland"],
    "CED": ["County Electoral Division", "England"],
    "COM": ["Community", "Wales"],
    "CTY": ["County", "England"],
    "CTYHIST": ["Historic County", "Great Britain"],
    "CTYLT": ["Lieutenancy County", "Great Britain"],
    "LOC": ["Locality", "Great Britain"],
    "LONB": ["London Borough", "England"],
    "MD": ["Metropolitan District", "England"],
    "NMD": ["Non-metropolitan District", "England"],
    "NPARK": ["National Park Great", "Britain"],
    "PAR": ["Civil Parish", "England and Scotland"],
    "RGN": ["Region", "England"],
    "UA": ["Unitary Authority", "England and Wales"],
    "WD": ["Electoral Ward/Division", "Great Britain"],
}

AREA_LOOKUP = [
    ("cty15cd", "cty", "cty15nm"),
    ("lad15cd", "laua", "lad15nm"),
    ("wd15cd", "ward", None),
    ("par15cd", "parish", None),
    ("hlth12cd", "hlth", "hlth12nm"),
    ("regd15cd", "rgd", "regd15nm"),
    ("rgn15cd", "rgn", "rgn15nm"),
    ("npark15cd", "park", "npark15nm"),
    ("bua11cd", "bua11", None),
    ("pcon15cd", "pcon", "pcon15nm"),
    ("eer15cd", "eer", "eer15nm"),
    ("pfa15cd", "pfa", "pfa15nm"),
    ("cty18cd", "cty", "cty18nm"),
    ("lad18cd", "laua", "lad18nm"),
    ("wd18cd", "ward", None),
    ("par18cd", "parish", None),
    ("hlth12cd", "hlth", "hlth12nm"),
    ("regd18cd", "rgd", "regd18nm"),
    ("rgn18cd", "rgn", "rgn18nm"),
    ("npark17cd", "park", "npark17nm"),
    ("bua11cd", "bua11", None),
    ("pcon18cd", "pcon", "pcon18nm"),
    ("eer18cd", "eer", "eer18nm"),
    ("pfa18cd", "pfa", "pfa18nm"),
]


@click.command("placenames")
@click.option("--es-index", default=PLACENAMES_INDEX)
@click.option("--url", default=settings.PLACENAMES_URL)
@click.option("--file", default=None)
def import_placenames(
    url=settings.PLACENAMES_URL, es_index=PLACENAMES_INDEX, file=None
):

    if settings.DEBUG:
        requests_cache.install_cache()

    es = db.get_db()

    if file:
        z = zipfile.ZipFile(file)
    else:
        r = requests.get(url, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))

    Placename.init(using=es)

    for f in z.filelist:
        if not f.filename.endswith(".csv"):
            continue

        print("[placenames] Opening %s" % f.filename)

        with z.open(f, "r") as pccsv:
            pccsv = io.TextIOWrapper(pccsv, encoding="latin1")
            reader = csv.DictReader(pccsv)
            placenames = defaultdict(list)
            for i in reader:
                for k in i:
                    if i[k] == "":
                        i[k] = None

                # population count
                i["splitind"] = bool(i["splitind"])

                # population count
                if i.get("popcnt"):
                    i["popcnt"] = int(i["popcnt"])

                # latitude and longitude
                for j in ["lat", "long"]:
                    if i[j]:
                        i[j] = float(i[j])
                        if i[j] == 99.999999 or i[j] == 0:
                            i[j] = None
                if i["lat"] and i["long"]:
                    i["location"] = {"lat": i["lat"], "lon": i["long"]}

                # get areas
                areas = {}
                for j in AREA_LOOKUP:
                    if j[0] in i:
                        areas[j[1]] = i[j[0]]
                        del i[j[0]]
                        if j[2] and j[2] in i:
                            del i[j[2]]
                i["areas"] = areas
                i["type"], i["country"] = PLACE_TYPES.get(
                    i["descnm"], [i["descnm"], "United Kingdom"]
                )
                placenames[i["place18cd"]].append(i)

            with BulkImporter(es, name="placenames") as importer:
                for records in placenames.values():
                    record = records[0]
                    record["alternative_names"] = list(
                        set([i["place18nm"] for i in records])
                    )
                    importer.add(
                        {
                            "_index": es_index,
                            "_type": "_doc",
                            "_op_type": "update",
                            "_id": record["place18cd"],
                            "doc_as_upsert": True,
                            "doc": record,
                        }
                    )

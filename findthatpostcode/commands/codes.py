"""
Import commands for the register of geographic codes and code history database
"""
import codecs
import csv
import io
import zipfile
from collections import defaultdict

import click
import requests
import requests_cache
import tqdm

from findthatpostcode import db, settings
from findthatpostcode.documents import Area, Entity
from findthatpostcode.utils import BulkImporter, process_date, process_float

ENTITY_INDEX = Entity.Index.name
AREA_INDEX = Area.Index.name
EQUIVALENT_CODES = {
    "ons": ["GEOGCDO", "GEOGNMO"],
    "mhclg": ["GEOGCDD", "GEOGNMD"],
    "nhs": ["GEOGCDH", "GEOGNMH"],
    "scottish_government": ["GEOGCDS", "GEOGNMS"],
    "welsh_government": ["GEOGCDWG", "GEOGNMWG", "GEOGNMWWG"],
}


@click.command("rgc")
@click.option("--url", default=settings.RGC_URL)
@click.option("--es-index", default=ENTITY_INDEX)
@click.option("--file", default=None)
def import_rgc(url=settings.RGC_URL, es_index=ENTITY_INDEX, file=None):
    if settings.DEBUG:
        requests_cache.install_cache()

    es = db.get_db()

    if file:
        z = zipfile.ZipFile(file)
    else:
        r = requests.get(url, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))

    Entity.init(using=es)

    for f in z.namelist():
        if not f.endswith(".csv"):
            continue
        with z.open(f, "r") as infile, BulkImporter(es, name="entities") as importer:
            reader = csv.DictReader(io.TextIOWrapper(infile, "utf-8-sig"))
            for record in reader:
                importer.add(
                    {
                        "_index": es_index,
                        "_op_type": "update",
                        "_id": record["Entity code"],
                        "doc_as_upsert": True,
                        "doc": Entity.from_csv(record).to_dict(),
                    }
                )


@click.command("chd")
@click.option("--url", default=settings.CHD_URL)
@click.option("--es-index", default=AREA_INDEX)
@click.option("--file", default=None)
@click.option("--encoding", default=settings.DEFAULT_ENCODING)
def import_chd(
    url=settings.CHD_URL,
    es_index=AREA_INDEX,
    file=None,
    encoding=settings.DEFAULT_ENCODING,
):
    if settings.DEBUG:
        requests_cache.install_cache()

    es = db.get_db()
    Area.init(using=es)

    if file:
        z = zipfile.ZipFile(file)
    else:
        r = requests.get(url, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))

    areas_cache = defaultdict(list)
    areas = {}

    change_history: str | None = None
    changes: str | None = None
    equivalents: str | None = None
    for f in z.namelist():
        if f.lower().startswith("changehistory") and f.lower().endswith(".csv"):
            change_history = f
        elif f.lower().startswith("changes") and f.lower().endswith(".csv"):
            changes = f
        elif f.lower().startswith("equivalents") and f.lower().endswith(".csv"):
            equivalents = f

    if change_history is None:
        raise Exception("Change history file not found")
    if changes is None:
        raise Exception("Changes file not found")
    if equivalents is None:
        raise Exception("Equivalents file not found")

    with z.open(change_history, "r") as infile:
        click.echo("Opening {}".format(infile.name))
        reader = csv.DictReader(io.TextIOWrapper(infile, encoding))
        for k, area in tqdm.tqdm(enumerate(reader)):
            areas_cache[area["GEOGCD"]].append(
                {
                    "code": area["GEOGCD"],
                    "name": area["GEOGNM"],
                    "name_welsh": area["GEOGNMW"] if area["GEOGNMW"] else None,
                    "statutory_instrument_id": area["SI_ID"] if area["SI_ID"] else None,
                    "statutory_instrument_title": area["SI_TITLE"]
                    if area["SI_TITLE"]
                    else None,
                    "date_start": process_date(area["OPER_DATE"][0:10], "%d/%m/%Y"),
                    "date_end": process_date(area["TERM_DATE"][0:10], "%d/%m/%Y"),
                    "parent": area["PARENTCD"] if area["PARENTCD"] else None,
                    "entity": area["ENTITYCD"],
                    "owner": area["OWNER"],
                    "active": area["STATUS"] == "live",
                    "areaehect": process_float(area["AREAEHECT"]),
                    "areachect": process_float(area["AREACHECT"]),
                    "areaihect": process_float(area["AREAIHECT"]),
                    "arealhect": process_float(area["AREALHECT"]),
                    "sort_order": area["GEOGCD"],
                    "predecessor": [],
                    "successor": [],
                    "equivalents": {},
                    "type": settings.ENTITIES.get(area["ENTITYCD"]),
                }
            )

    for area_code, area_history in tqdm.tqdm(areas_cache.items()):
        if len(area_history) == 1:
            area = area_history[0]
            area["alternative_names"] = []
            if area["name"]:
                area["alternative_names"].append(area["name"])
            if area["name_welsh"]:
                area["alternative_names"].append(area["name_welsh"])
        else:
            area_history = sorted(area_history, key=lambda x: x["date_start"])
            area = area_history[-1]
            area["date_start"] = area_history[0]["date_start"]
            area["alternative_names"] = []
            for h in area_history:
                if h["name"] and h["name"] not in area["alternative_names"]:
                    area["alternative_names"].append(h["name"])
                if h["name_welsh"] and h["name_welsh"] not in area["alternative_names"]:
                    area["alternative_names"].append(h["name_welsh"])
        areas[area_code] = area

    with z.open(changes, "r") as infile:
        reader = csv.DictReader(io.TextIOWrapper(infile, encoding))
        click.echo("Opening {}".format(infile.name))
        for k, area in tqdm.tqdm(enumerate(reader)):
            if area["GEOGCD_P"] == "":
                continue
            if area["GEOGCD"] in areas:
                areas[area["GEOGCD"]]["predecessor"].append(area["GEOGCD_P"])
            if area["GEOGCD_P"] in areas:
                areas[area["GEOGCD_P"]]["successor"].append(area["GEOGCD"])

    with z.open(equivalents, "r") as infile:
        reader = csv.DictReader(io.TextIOWrapper(infile, encoding))
        click.echo("Opening {}".format(infile.name))
        for area in tqdm.tqdm(reader):
            if area["GEOGCD"] not in areas:
                continue
            for k, v in EQUIVALENT_CODES.items():
                if area[v[0]]:
                    areas[area["GEOGCD"]]["equivalents"][k] = area[v[0]]

    with BulkImporter(es, name="areas", limit=50000) as importer:
        for area_code, area in tqdm.tqdm(areas.items()):
            importer.add(
                {
                    "_index": es_index,
                    "_op_type": "update",
                    "_id": area_code,
                    "doc_as_upsert": True,
                    "doc": area,
                }
            )


@click.command("msoanames")
@click.option("--url", default=settings.MSOA_URL)
@click.option("--es-index", default=AREA_INDEX)
@click.option("--file", default=None)
@click.option("--encoding", default="utf-8-sig")
def import_msoa_names(
    url=settings.MSOA_URL, es_index=AREA_INDEX, file=None, encoding="utf-8-sig"
):
    if settings.DEBUG:
        requests_cache.install_cache()

    es = db.get_db()

    if file:
        file = open(file, encoding=encoding)
    else:
        r = requests.get(url, stream=True)
        file = codecs.iterdecode(r.iter_lines(), encoding=encoding)

    reader = csv.DictReader(file)
    with BulkImporter(es, name="msoa names", limit=50000) as importer:
        for k, area in tqdm.tqdm(enumerate(reader)):
            alt_names = [area["msoa11hclnm"]]
            if area["msoa11hclnmw"]:
                alt_names.append(area["msoa11hclnmw"])
            importer.add(
                {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": area["msoa11cd"],
                    "doc": {
                        "name": area["msoa11hclnm"],
                        "name_welsh": area["msoa11hclnmw"]
                        if area["msoa11hclnmw"]
                        else None,
                        "alternative_names": alt_names,
                    },
                }
            )

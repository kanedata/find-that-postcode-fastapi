"""
Import commands for the register of geographic codes and code history database
"""
import codecs
import csv
import datetime
import io
import zipfile

import click
import requests
import requests_cache
from typer import progressbar

from findthatpostcode.commands.import_app import app
from findthatpostcode.database import get_db, upsert_statement
from findthatpostcode.models import Area, Entity
from findthatpostcode.settings import (
    CHD_URL,
    DEFAULT_ENCODING,
    ENTITIES,
    MSOA_URL,
    RGC_URL,
)


def process_date(value, date_format="%d/%m/%Y"):
    if value in ["", "n/a"]:
        return None
    return datetime.datetime.strptime(value, date_format)


def process_int(value):
    if value in ["", "n/a"]:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return int(value)


def process_float(value):
    if value in ["", "n/a"]:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return float(value)


@app.command()
def rgc(url: str = RGC_URL, use_cache: bool = True):
    """
    Import from the Register of Geographic Codes (RGC)
    """

    if use_cache:
        session = requests_cache.CachedSession("demo_cache")
    else:
        session = requests.Session()

    r = session.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    db = get_db()

    for conn in db:
        for f in z.namelist():
            if not f.endswith(".csv"):
                continue
            with z.open(f, "r") as infile:
                reader = csv.DictReader(io.TextIOWrapper(infile, "utf-8-sig"))
                entities = []
                for entity in reader:

                    # tidy up a couple of records
                    entity["Related entity codes"] = (
                        entity["Related entity codes"].replace("n/a", "").split(", ")
                    )

                    entities.append(
                        {
                            "code": entity["Entity code"],
                            "name": entity["Entity name"],
                            "abbreviation": entity["Entity abbreviation"],
                            "theme": entity["Entity theme"],
                            "coverage": entity["Entity coverage"],
                            "related_codes": entity["Related entity codes"],
                            "status": entity["Status"],
                            "live_instances": process_int(
                                entity["Number of live instances"]
                            ),
                            "archived_instances": process_int(
                                entity["Number of archived instances"]
                            ),
                            "crossborder_instances": process_int(
                                entity["Number of cross-border instances"]
                            ),
                            "last_modified": process_date(
                                entity["Date of last instance change"]
                            ),
                            "current_code_first": entity[
                                "Current code (first in range)"
                            ],
                            "current_code_last": entity["Current code (last in range)"],
                            "reserved_code": entity["Reserved code (for CHD use)"],
                            "owner": entity.get("Entity owner"),
                            "date_introduced": process_date(
                                entity["Date entity introduced on RGC"]
                            ),
                            "date_start": process_date(entity["Entity start date"]),
                            "type": ENTITIES.get(entity["Entity code"]),
                        }
                    )

                upsert_stmt = upsert_statement(Entity, [Entity.code])
                conn.execute(upsert_stmt, entities)
            conn.commit()
            conn.close()


@app.command()
def chd(url: str = CHD_URL, use_cache: bool = True, encoding: str = DEFAULT_ENCODING):
    """
    Import from the Register of Geographic Codes (RGC)
    """

    if use_cache:
        session = requests_cache.CachedSession("demo_cache")
    else:
        session = requests.Session()

    r = session.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    areas = {}

    change_history = None
    changes = None
    equivalents = None
    for f in z.namelist():
        if f.lower().startswith("changehistory") and f.lower().endswith(".csv"):
            change_history = f
        elif f.lower().startswith("changes") and f.lower().endswith(".csv"):
            changes = f
        elif f.lower().startswith("equivalents") and f.lower().endswith(".csv"):
            equivalents = f

    with z.open(change_history, "r") as infile:
        click.echo("Opening {}".format(infile.name))
        reader = csv.DictReader(io.TextIOWrapper(infile, encoding))
        with progressbar(enumerate(reader)) as progress:
            for k, area in progress:
                areas[area["GEOGCD"]] = {
                    "code": area["GEOGCD"],
                    "name": area["GEOGNM"] or None,
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
                    "type": ENTITIES.get(area["ENTITYCD"]),
                }

    with z.open(changes, "r") as infile:
        reader = csv.DictReader(io.TextIOWrapper(infile, encoding))
        click.echo("Opening {}".format(infile.name))
        with progressbar(enumerate(reader)) as progress:
            for k, area in progress:
                if area["GEOGCD_P"] == "":
                    continue
                if area["GEOGCD"] in areas:
                    areas[area["GEOGCD"]]["predecessor"].append(area["GEOGCD_P"])
                if area["GEOGCD_P"] in areas:
                    areas[area["GEOGCD_P"]]["successor"].append(area["GEOGCD"])

    equiv = {
        "ons": ["GEOGCDO", "GEOGNMO"],
        "mhclg": ["GEOGCDD", "GEOGNMD"],
        "nhs": ["GEOGCDH", "GEOGNMH"],
        "scottish_government": ["GEOGCDS", "GEOGNMS"],
        "welsh_government": ["GEOGCDWG", "GEOGNMWG", "GEOGNMWWG"],
    }
    with z.open(equivalents, "r") as infile:
        reader = csv.DictReader(io.TextIOWrapper(infile, encoding))
        click.echo("Opening {}".format(infile.name))
        with progressbar(reader) as progress:
            for area in progress:
                if area["GEOGCD"] not in areas:
                    continue
                for k, v in equiv.items():
                    if area[v[0]]:
                        areas[area["GEOGCD"]]["equivalents"][k] = area[v[0]]

    db = get_db()
    for conn in db:
        upsert_stmt = upsert_statement(Area, [Area.code])
        conn.execute(upsert_stmt, list(areas.values()))
        conn.commit()
        conn.close()


@app.command()
def msoa_names(url: str = MSOA_URL, use_cache: bool = True):
    """
    Import names for MSOAs from the House of Commons Library
    """

    if use_cache:
        session = requests_cache.CachedSession("demo_cache")
    else:
        session = requests.Session()

    r = session.get(url, stream=True)

    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), "utf-8-sig"))
    db = get_db()
    for conn in db:
        with progressbar(enumerate(reader)) as progress:
            for k, area in progress:
                conn.execute(
                    Area.__table__.update()
                    .where(Area.code == area["msoa11cd"])
                    .values(
                        name=area["msoa11hclnm"],
                        name_welsh=area["msoa11hclnmw"]
                        if area["msoa11hclnmw"]
                        else None,
                    )
                )
        conn.commit()
        conn.close()

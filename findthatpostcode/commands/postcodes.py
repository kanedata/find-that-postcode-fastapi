"""
Import commands for the register of geographic codes and code history database
"""

import csv
import io
import zipfile

import click
import requests
import requests_cache
from tqdm import tqdm

from findthatpostcode import db, settings
from findthatpostcode.documents import Postcode, PostcodeSource
from findthatpostcode.utils import BulkImporter

PC_INDEX = Postcode.Index.name


@click.command("nspl")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=settings.NSPL_URL)
@click.option("--file", default=None)
def import_nspl(url=settings.NSPL_URL, es_index=PC_INDEX, file=None):
    return import_from_postcode_file(
        url=url,
        es_index=es_index,
        file=file,
        filetype=PostcodeSource.NSPL,
        file_location="Data/multi_csv/NSPL",
    )


@click.command("onspd")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=settings.ONSPD_URL)
@click.option("--file", default=None)
def import_onspd(url=settings.ONSPD_URL, es_index=PC_INDEX, file=None):
    return import_from_postcode_file(
        url=url,
        es_index=es_index,
        file=file,
        filetype=PostcodeSource.ONSPD,
        file_location="Data/multi_csv/ONSPD",
    )


@click.command("nhspd")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=settings.NHSPD_URL)
@click.option("--file", default=None)
def import_nhspd(url=settings.NHSPD_URL, es_index=PC_INDEX, file=None):
    return import_from_postcode_file(
        url=url,
        es_index=es_index,
        file=file,
        filetype=PostcodeSource.NHSPD,
        file_location="Data/",
    )


@click.command("pcon")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=settings.PCON_URL)
@click.option("--file", default=None)
def import_pcon(url=settings.PCON_URL, es_index=PC_INDEX, file=None):
    return import_from_postcode_file(
        url=url,
        es_index=es_index,
        file=file,
        filetype=PostcodeSource.PCON,
        file_location="pcd_pcon_",
    )


def import_from_postcode_file(
    url=settings.NSPL_URL,
    es_index=PC_INDEX,
    file=None,
    filetype: PostcodeSource = PostcodeSource.NSPL,
    file_location: str = "Data/multi_csv/NSPL",
):
    if settings.DEBUG:
        requests_cache.install_cache()

    # set up the elasticsearch client and index
    es = db.get_db()
    Postcode.init(using=es)

    if file:
        z = zipfile.ZipFile(file)
    else:
        r = requests.get(url, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))

    fieldnames = None
    if filetype == PostcodeSource.NHSPD:
        fieldnames = settings.NHSPD_FIELDNAMES

    for f in z.filelist:
        if not f.filename.endswith(".csv") or not f.filename.startswith(file_location):
            continue

        print(f"[postcodes] Opening {f.filename}")

        with z.open(f, "r") as pccsv, BulkImporter(es, name="postcodes") as importer:
            pccsv = io.TextIOWrapper(pccsv)
            reader = csv.DictReader(pccsv, fieldnames=fieldnames)
            for record in tqdm(reader):
                if filetype == PostcodeSource.PCON:
                    record = {
                        "pcds": record["pcd"],
                        "pcon25": record["pconcd"],
                    }

                importer.add(
                    {
                        "_index": es_index,
                        "_op_type": "update",
                        "_id": record["pcds"],
                        "doc_as_upsert": True,
                        "doc": {
                            filetype.value: Postcode.from_csv(record).to_dict(),
                        },
                    }
                )

                if settings.DEBUG and (len(importer) >= 100):
                    break

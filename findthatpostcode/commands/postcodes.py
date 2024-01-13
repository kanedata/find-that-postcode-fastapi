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
from findthatpostcode.documents import Postcode
from findthatpostcode.utils import BulkImporter

PC_INDEX = Postcode.Index.name


@click.command("nspl")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=settings.NSPL_URL)
@click.option("--file", default=None)
def import_nspl(url=settings.NSPL_URL, es_index=PC_INDEX, file=None):
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

    for f in z.filelist:
        if not f.filename.endswith(".csv") or not f.filename.startswith(
            "Data/multi_csv/NSPL"
        ):
            continue

        print(f"[postcodes] Opening {f.filename}")

        with z.open(f, "r") as pccsv, BulkImporter(es, name="postcodes") as importer:
            pccsv = io.TextIOWrapper(pccsv)
            reader = csv.DictReader(pccsv)
            for record in tqdm(reader):
                importer.add(
                    {
                        "_index": es_index,
                        "_op_type": "update",
                        "_id": record["pcds"],
                        "doc_as_upsert": True,
                        "doc": Postcode.from_csv(record).to_dict(),
                    }
                )

                if settings.DEBUG and (len(importer) >= 100):
                    break

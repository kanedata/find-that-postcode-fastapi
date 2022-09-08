"""
Import commands for area boundaries
"""

import click
import requests
import requests_cache
import shapely.geometry
import tqdm

from findthatpostcode import settings, db
from findthatpostcode.documents import Entity, Area
from findthatpostcode.utils import BulkImporter

AREA_INDEX = Area.Index.name


@click.command("boundaries")
@click.option("--es-index", default=AREA_INDEX)
@click.option("--code-field", default=None)
@click.option("--examine/--no-examine", default=False)
@click.argument("urls", nargs=-1)
def import_boundaries(urls, examine=False, code_field=None, es_index=AREA_INDEX):

    if settings.DEBUG:
        requests_cache.install_cache()

    es = db.get_db()

    for url in urls:
        import_boundary(es, url, examine, es_index, code_field)


def import_boundary(es, url, examine=False, es_index=AREA_INDEX, code_field=None):
    r = requests.get(url, stream=True)
    boundaries = r.json()
    errors = []

    # find the code field for a boundary
    if len(boundaries.get("features", [])) == 0:
        errors.append(
            "[ERROR][{}] Features not found in file".format(
                url,
            )
        )
    if len(boundaries.get("features", [])) > 0 and not code_field:
        test_boundary = boundaries.get("features", [])[0]
        code_fields = []
        for k in test_boundary.get("properties", {}):
            if k.lower().endswith("cd"):
                code_fields.append(k)
        if len(code_fields) == 1:
            code_field = code_fields[0]
        elif len(code_fields) == 0:
            errors.append(
                "[ERROR][{}] No code field found in file".format(
                    url,
                )
            )
        else:
            errors.append(
                "[ERROR][{}] Too many code fields found in file".format(
                    url,
                )
            )
            errors.append(
                "[ERROR][{}] Code fields: {}".format(url, "; ".join(code_fields))
            )

    if len(errors) > 0:
        if examine:
            for e in errors:
                print(e)
        else:
            raise ValueError("; ".join(errors))

    code = code_field.lower().replace("cd", "")

    if examine:
        print("[{}] Opened file: [{}]".format(code, url))
        print("[{}] Looking for code field: [{}]".format(code, code_field))
        print("[{}] Geojson type: [{}]".format(code, boundaries["type"]))
        print("[{}] Number of features [{}]".format(code, len(boundaries["features"])))
        for k, i in enumerate(boundaries["features"][:5]):
            print("[{}] Feature {} type {}".format(code, k, i["type"]))
            print(
                "[{}] Feature {} properties {}".format(
                    code, k, list(i["properties"].keys())
                )
            )
            print(
                "[{}] Feature {} geometry type {}".format(
                    code, k, i["geometry"]["type"]
                )
            )
            print(
                "[{}] Feature {} geometry length {}".format(
                    code, k, len(str(i["geometry"]["coordinates"]))
                )
            )
            if code_field in i["properties"]:
                print(
                    "[{}] Feature {} Code {}".format(
                        code, k, i["properties"][code_field]
                    )
                )
            else:
                print(
                    "[ERROR][{}] Feature {} Code field not found".format(
                        code,
                        k,
                    )
                )

    else:
        print("[{}] Opened file: [{}]".format(code, url))
        print("[{}] {} features to import".format(code, len(boundaries["features"])))

        with BulkImporter(name="boundaries", es=es) as importer:
            for k, i in tqdm.tqdm(
                enumerate(boundaries["features"]), total=len(boundaries["features"])
            ):
                shp = shapely.geometry.shape(i["geometry"]).buffer(0)
                boundary = {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": i["properties"][code_field],
                    "doc": {
                        "boundary": shp.wkt,
                        "has_boundary": True,
                    },
                }
                importer.add(boundary)

            for error in importer.errors:
                print(
                    " - {} {}".format(
                        error.get("update", {}).get("_id", ""),
                        error.get("update", {})
                        .get("error", {})
                        .get("caused_by", {})
                        .get("type", ""),
                    )
                )

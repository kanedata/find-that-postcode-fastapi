"""
Import commands for the register of geographic codes and code history database
"""
import csv
import datetime
import hashlib
import io
import zipfile

import requests
import requests_cache

from findthatpostcode.commands.import_app import app
from findthatpostcode.database import get_db, upsert_statement
from findthatpostcode.models import Postcode
from findthatpostcode.settings import NSPL_URL


@app.command()
def nspl(url: str = NSPL_URL, use_cache: bool = True):
    """
    Import the National Statistical Postcode Lookup (NSPL)
    """

    if use_cache:
        session = requests_cache.CachedSession("demo_cache")
    else:
        session = requests.Session()

    r = session.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    postcodes = []

    db = get_db()

    for conn in db:
        for f in z.filelist:
            if not f.filename.endswith(".csv") or not f.filename.startswith(
                "Data/multi_csv/NSPL_"
            ):
                continue

            print("[postcodes] Opening %s" % f.filename)

            pcount = 0
            with z.open(f, "r") as pccsv:
                pccsv = io.TextIOWrapper(pccsv)
                reader = csv.DictReader(pccsv)
                now = datetime.datetime.now()
                for i in reader:

                    # null any blank fields (or ones with a dummy code in)
                    for k in i:
                        if i[k] == "" or i[k] in [
                            "E99999999",
                            "S99999999",
                            "W99999999",
                            "N99999999",
                        ]:
                            i[k] = None

                    # date fields
                    for j in ["dointr", "doterm"]:
                        if i[j]:
                            i[j] = datetime.datetime.strptime(i[j], "%Y%m")

                    # latitude and longitude
                    for j in ["lat", "long"]:
                        if i[j]:
                            i[j] = float(i[j])
                            if i[j] == 99.999999:
                                i[j] = None
                    i["geom"] = None
                    if i["lat"] and i["long"]:
                        i["geom"] = f"POINT({i['long']} {i['lat']})"

                    # integer fields
                    for j in ["oseast1m", "osnrth1m", "usertype", "osgrdind", "imd"]:
                        if i[j]:
                            i[j] = int(i[j])

                    # add postcode hash
                    i["hash"] = hashlib.md5(
                        i["pcds"].lower().replace(" ", "").encode()
                    ).hexdigest()
                    i["hash4"] = i["hash"][:4]

                    # add the active and updated fields
                    i["active"] = True
                    i["updated"] = now

                    postcodes.append(i)
                    pcount += 1

                # save the postcodes
                upsert_stmt = upsert_statement(Postcode, [Postcode.pcd])
                conn.execute(upsert_stmt, postcodes)
                postcodes = []
        conn.commit()
        conn.close()

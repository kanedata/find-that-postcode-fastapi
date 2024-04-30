from typing import Any

from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import Route as StarletteRoute

from findthatpostcode import api, crud, graphql
from findthatpostcode.db import get_db
from findthatpostcode.routers import areatypes, postcodes, tools
from findthatpostcode.utils import templates

description = """
This site presents data on UK postcodes and geographical areas, based on open data released by
the [Office for National Statistics](https://findthatpostcode.uk/about) and
[Ordnance Survey](https://findthatpostcode.uk/about).

It is intended to help the process of enhancing existing data sets, for example by
allowing someone to lookup which local authority a postcode is in.
    
## Data sources

- **Postcode data**: [NSPL](https://geoportal.statistics.gov.uk/datasets/national-statistics-postcode-lookup-november-2019)
- **Area data**: [Code History Database](https://geoportal.statistics.gov.uk/datasets/code-history-database-june-2019-for-the-united-kingdom) and [Register of Geographic Codes](https://geoportal.statistics.gov.uk/datasets/register-of-geographic-codes-june-2019-for-the-united-kingdom)
- **Boundary data**: [ONS Geoportal](http://geoportal.statistics.gov.uk/datasets?q=Latest_Boundaries&sort_by=name&sort_order=asc)
- **Placenames**: [Index of Place Names in Great Britain](https://geoportal.statistics.gov.uk/datasets/index-of-place-names-in-great-britain-september-2019)
- **MSOA names**: [House of Commons Library](https://visual.parliament.uk/msoanames) ([Open Parliament Licence](https://www.parliament.uk/site-information/copyright/open-parliament-licence/))

[Postcode data from ONS used under Open Government License](https://www.ons.gov.uk/methodology/geography/licences)

Contains OS data © Crown copyright and database right 2022

Contains Royal Mail data © Royal Mail copyright and database right 2022

Contains National Statistics data © Crown copyright and database right 2022

Northern Ireland postcodes are included based on the 
[Northern Ireland End User Licence](https://www.ons.gov.uk/methodology/geography/licences).
The licence covers internal use of the data. Commercial use may require additional permission.
"""


app = FastAPI(
    title="Find that Postcode API",
    description=description,
    version="1.0.0",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Kane Data Limited",
        "url": "https://dkane.net/",
        "email": "info@findthatpostcode.uk",
    },
    openapi_tags=[
        {
            "name": "Get postcode",
            "description": "Postcode lookup",
        }
    ],
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    # license_info={
    #     "name": "Apache 2.0",
    #     "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    # },
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api.router)
app.include_router(graphql.router, prefix="/graphql", include_in_schema=False)
app.include_router(tools, prefix="/tools")
app.include_router(postcodes, prefix="/postcodes")
app.include_router(areatypes, prefix="/areatypes")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html.j2")


@app.get("/search/", response_class=HTMLResponse, include_in_schema=False)
def search(request: Request, db: Elasticsearch = Depends(get_db)):
    print(db)
    q = request.query_params.get("q", "")
    context: dict[str, Any] = {"q": q}
    if q:
        areas = crud.search_areas(db, q)
        context["result"] = list(zip(areas.result, areas.scores))
        context["total"] = areas.result_count
    return templates.TemplateResponse(request, "areasearch.html.j2", context)


@app.get("/addtocsv/", response_class=RedirectResponse, include_in_schema=False)
def addtocsv_redirect(request: Request):
    return RedirectResponse(request.url_for("tools_addtocsv"), status_code=302)


@app.get("/url-list")
def get_all_urls():
    url_list = [
        {"path": route.path, "name": route.name}
        for route in app.routes
        if isinstance(route, StarletteRoute)
    ]
    return url_list

import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from findthatpostcode import api, graphql, settings

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
    version="0.0.1",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "David Kane",
        "url": "https://dkane.net/",
        "email": "info@findthatpostcode.uk",
    },
    openapi_tags=[
        {
            "name": "Get postcode",
            "description": "Postcode lookup",
        }
    ]
    # license_info={
    #     "name": "Apache 2.0",
    #     "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    # },
)

templates = Jinja2Templates(directory="templates")
templates.env.globals.update(
    dict(
        now=datetime.datetime.now(),
        key_area_types=settings.KEY_AREA_TYPES,
        other_codes=settings.OTHER_CODES,
        area_types=settings.AREA_TYPES,
    )
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api.router)
app.include_router(graphql.router, prefix="/graphql", include_in_schema=False)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse("index.html.j2", {"request": request})

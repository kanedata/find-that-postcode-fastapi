import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from findthatpostcode import api, graphql, settings

app = FastAPI(
    title="Find that Postcode API",
    # description=description,
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
app.include_router(graphql.router, prefix="/graphql")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html.j2", {"request": request})

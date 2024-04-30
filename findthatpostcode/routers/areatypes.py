from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from findthatpostcode import crud, settings
from findthatpostcode.db import get_db
from findthatpostcode.utils import templates

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def all_areatypes(request: Request, db: Elasticsearch = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "areatypes.html.j2",
        {"areatypes": crud.get_all_areatypes(db)},
    )


@router.get("/{areacode}", response_class=HTMLResponse, include_in_schema=False)
def get_areatype(areacode: str, request: Request, db: Elasticsearch = Depends(get_db)):
    areatype = settings.AREA_TYPES.get(areacode)
    return templates.TemplateResponse(
        request,
        "areatype.html.j2",
        {
            "result": {
                **areatype,
                "attributes": {
                    **areatype,
                    "count_areas": 0,
                },
                "relationships": {},
                "count_areas": 0,
            },
        },
    )

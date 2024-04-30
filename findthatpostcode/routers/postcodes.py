from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from findthatpostcode import crud
from findthatpostcode.db import get_db
from findthatpostcode.schemas import Postcode
from findthatpostcode.utils import templates

router = APIRouter(include_in_schema=False)


@router.get(
    "/{postcode}.html",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def get_postcode_html(
    postcode: str,
    request: Request,
    db: Elasticsearch = Depends(get_db),
):
    return templates.TemplateResponse(
        request,
        "postcode.html.j2",
        {"result": crud.get_postcode(db, postcode)},
    )


@router.get("/{postcode}", response_model=Postcode, include_in_schema=False)
@router.get(
    "/{postcode}.json",
    response_model=Postcode,
    include_in_schema=False,
)
def get_postcode_json(
    postcode: str,
    request: Request,
    db: Elasticsearch = Depends(get_db),
):
    return crud.get_postcode(db, postcode)

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from findthatpostcode.utils import templates

router = APIRouter(include_in_schema=False, default_response_class=HTMLResponse)


@router.get("/merge-geojson")
def geojson_merge(request: Request):
    return templates.TemplateResponse(request, "merge-geojson.html.j2")


@router.get("/reduce-geojson")
def geojson_reduce(request: Request):
    return templates.TemplateResponse(request, "reduce-geojson.html.j2")


@router.get("/addtocsv", name="tools_addtocsv")
def addtocsv(request: Request):
    return templates.TemplateResponse(request, "addtocsv.html.j2")

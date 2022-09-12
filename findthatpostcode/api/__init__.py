import logging
from typing import List

from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query, status, Form
from sqlalchemy.orm import Session

from findthatpostcode import crud

from findthatpostcode.db import get_db
from findthatpostcode.schemas import Area, HTTPNotFoundError, NearestPoint, Postcode

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": HTTPNotFoundError,
        }
    },
)


@router.get(
    "/postcodes/{postcode}.json",
    response_model=Postcode,
    tags=["Get postcode"],
)
async def read_postcode(postcode: str, db: Elasticsearch = Depends(get_db)):
    logger.info(postcode)
    postcode_item = crud.get_postcode(db, postcode)
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postcode {} not found".format(postcode),
        )
    return postcode_item


@router.get("/hash/{hash}", tags=["Postcode hash"], include_in_schema=False)
@router.get("/hash/{hash}.json", tags=["Postcode hash"], include_in_schema=False)
async def single_hash(
    hash: str, fields: list[str] = Query([]), db: Session = Depends(get_db)
):
    postcode_items = crud.get_postcode_by_hash(db, [hash], fields=fields)
    return {"data": list(postcode_items)}


@router.post(
    "/hashes.json",
    tags=["Postcode hash"],
    include_in_schema=False,
    name="multiple_hash",
)
async def multiple_hash(
    hash: list[str] = Form([]),
    properties: list[str] = Form([]),
    db: Session = Depends(get_db),
):
    postcode_items = crud.get_postcode_by_hash(db, hash, fields=properties)
    return {"data": list(postcode_items)}


@router.get(
    "/points/{lat},{long}.json",
    response_model=NearestPoint,
    tags=["Get a point"],
    description="Get nearest postcode to a Lat, Long",
)
async def find_nearest_point(lat: float, long: float, db: Session = Depends(get_db)):
    postcode_item = crud.get_nearest_postcode(db, lat, long)
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No postcode found".format(),
        )
    return postcode_item


@router.get(
    "/areas/{areacode}.json",
    response_model=Area,
    tags=["Areas"],
    description="Get data about an area",
)
async def get_area(areacode: str, db: Session = Depends(get_db)):
    area = crud.get_area(db, areacode)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No area found for {}".format(areacode),
        )
    return area

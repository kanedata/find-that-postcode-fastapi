import logging
from typing import List

from botocore.client import BaseClient
from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from mypy_boto3_s3.client import S3Client
from pydantic_geojson import FeatureModel
from sqlalchemy.orm import Session

from findthatpostcode import crud
from findthatpostcode.db import get_db, get_s3_client
from findthatpostcode.schemas import (
    Area,
    HTTPNotFoundError,
    NearestPoint,
    Postcode,
    PostcodeHashResults,
)

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


@router.get(
    "/hash/{hash}",
    tags=["Postcode hash"],
    include_in_schema=False,
    response_model=PostcodeHashResults,
)
@router.get(
    "/hash/{hash}.json",
    tags=["Postcode hash"],
    include_in_schema=False,
    response_model=PostcodeHashResults,
)
async def single_hash(
    hash: str, fields: list[str] = Query([]), db: Elasticsearch = Depends(get_db)
):
    postcode_items = crud.get_postcode_by_hash(db, [hash], fields=fields)
    print(postcode_items)
    return {"data": list(postcode_items)}


@router.post(
    "/hashes.json",
    tags=["Postcode hash"],
    include_in_schema=False,
    name="multiple_hash",
    response_model=PostcodeHashResults,
)
async def multiple_hash(
    hash: list[str] = Form([]),
    properties: list[str] = Form([]),
    db: Elasticsearch = Depends(get_db),
):
    postcode_items = crud.get_postcode_by_hash(db, hash, fields=properties)
    return {"data": list(postcode_items)}


@router.get(
    "/points/{lat},{long}.json",
    response_model=NearestPoint,
    tags=["Get a point"],
    description="Get nearest postcode to a Lat, Long",
)
async def find_nearest_point(
    lat: float, long: float, db: Elasticsearch = Depends(get_db)
):
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
async def get_area(areacode: str, db: Elasticsearch = Depends(get_db)):
    area = crud.get_area(db, areacode)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No area found for {}".format(areacode),
        )
    return area


@router.get(
    "/areas/{areacode}.geojson",
    response_model=FeatureModel,
    tags=["Areas"],
    description="Get an area's boundary as a geojson file",
)
async def get_area_boundary(
    areacode: str,
    db: Elasticsearch = Depends(get_db),
    client: S3Client = Depends(get_s3_client),
):
    area = crud.get_area_boundary(db, client, areacode)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No area found for {}".format(areacode),
        )
    return area


@router.get(
    "/areas/search.json",
    response_model=Area,
    tags=["Areas"],
    description="Search areas",
)
async def search_areas(areacode: str, db: Elasticsearch = Depends(get_db)):
    area = crud.get_area(db, areacode)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No area found for {}".format(areacode),
        )
    return area

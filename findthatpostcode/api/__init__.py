from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from findthatpostcode import crud
from findthatpostcode.database import get_db
from findthatpostcode.schemas import HTTPNotFoundError, NearestPoint, Postcode, Area

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
async def read_postcode(postcode: str, db: Session = Depends(get_db)):
    postcode_item = crud.get_postcode(db, postcode)
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postcode {} not found".format(postcode),
        )
    return postcode_item


@router.get("/hash/{hash}", tags=["Postcode hash"])
@router.get("/hash/{hash}.json", tags=["Postcode hash"])
async def single_hash(
    hash: str, fields: list[str] = Query([]), db: Session = Depends(get_db)
):
    postcode_items = crud.get_postcode_by_hash(db, [hash], fields=fields)
    return {"data": list(postcode_items)}


@router.get("/hashes.json", tags=["Postcode hash"])
async def multiple_hash(
    hashes: list[str] = Query([]),
    fields: list[str] = Query([]),
    db: Session = Depends(get_db),
):
    postcode_items = crud.get_postcode_by_hash(db, hashes, fields=fields)
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

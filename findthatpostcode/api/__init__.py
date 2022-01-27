from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from findthatpostcode import crud
from findthatpostcode.database import get_db
from findthatpostcode.schemas import HTTPNotFoundError, NearestPoint, Postcode

router = APIRouter(
    prefix="/api/v1",
    tags=["postcodes"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "model": HTTPNotFoundError,
        }
    },
)


@router.get("/postcodes/{postcode}.json", response_model=Postcode)
async def read_postcode(postcode: str, db: Session = Depends(get_db)):
    postcode_item = crud.get_postcode(db, postcode)
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postcode {} not found".format(postcode),
        )
    return postcode_item


@router.get("/hash/{hash}")
@router.get("/hash/{hash}.json")
async def single_hash(
    hash: str, fields: list[str] = Query([]), db: Session = Depends(get_db)
):
    postcode_items = crud.get_postcode_by_hash(db, [hash], fields=fields)
    return {"data": list(postcode_items)}


# @router.get("/hashes.json", response_model=Postcode)
# async def multi_hash(db: Session = Depends(get_db)):
#     postcode_item = get_postcode(db, postcode)
#     if not postcode_item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Postcode {} not found".format(postcode),
#         )
#     return postcode_item


@router.get(
    "/points/{lat},{long}.json",
    response_model=NearestPoint,
    tags=["points"],
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

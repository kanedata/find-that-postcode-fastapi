from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from findthatpostcode.crud import get_nearest_postcode, get_postcode
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
    postcode_item = get_postcode(db, postcode)
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postcode {} not found".format(postcode),
        )
    return postcode_item


@router.get("/points/{lat},{long}.json", response_model=NearestPoint)
async def find_nearest_point(lat: float, long: float, db: Session = Depends(get_db)):
    postcode_item = get_nearest_postcode(db, lat, long)
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No postcode found".format(),
        )
    return postcode_item

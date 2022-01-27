from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session

from findthatpostcode import models
from findthatpostcode.database import get_db
from findthatpostcode.schemas import Postcode, HTTPNotFoundError

router = APIRouter(
    prefix="/api/v1",
    tags=["postcodes"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found", "model": HTTPNotFoundError}},
)


@router.get("/postcodes/{postcode}.json", response_model=Postcode)
async def read_postcode(postcode: str, db: Session = Depends(get_db)):
    postcode_item = (
        db.query(models.Postcode)
        .filter(models.Postcode.pcds == models.Postcode.parse_id(postcode))
        .first()
    )
    if not postcode_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postcode {} not found".format(postcode)
        )
    return postcode_item

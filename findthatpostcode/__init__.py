from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from findthatpostcode import models
from findthatpostcode.database import get_db
from findthatpostcode.schemas import Postcode

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/postcodes/{postcode}.json", response_model=Postcode)
def read_postcode(postcode: str, db: Session = Depends(get_db)):
    postcode_item = (
        db.query(models.Postcode)
        .filter(models.Postcode.pcds == models.Postcode.parse_id(postcode))
        .first()
    )
    if not postcode_item:
        raise HTTPException(
            status_code=404, detail="Postcode {} not found".format(postcode)
        )
    return postcode_item

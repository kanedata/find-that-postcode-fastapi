from datetime import date
from typing import Optional

from pydantic import BaseModel


class Postcode(BaseModel):
    pcd: str
    bua11: Optional[str] = None
    buasd11: Optional[str] = None
    ccg: Optional[str] = None
    ced: Optional[str] = None
    ctry: Optional[str] = None
    dointr: Optional[date] = None
    doterm: Optional[date] = None
    eer: Optional[str] = None
    hash: Optional[str] = None
    hlthau: Optional[str] = None
    imd: Optional[int] = None
    itl: Optional[str] = None
    laua: Optional[str] = None
    lep1: Optional[str] = None
    lep2: Optional[str] = None

    class Config:
        orm_mode = True

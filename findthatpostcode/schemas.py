from datetime import date
from typing import Optional

import strawberry
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


class HTTPNotFoundError(BaseModel):
    detail: str


@strawberry.type
@dataclass
class Postcode:
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
    laua: Optional[str] = Field(None, title="Local Authority GSS Code")
    lep1: Optional[str] = None
    lep2: Optional[str] = None

    class Config:
        orm_mode = True


@dataclass
class Point:
    point_lat: float
    point_long: float


@strawberry.type
@dataclass
class NearestPoint(Postcode, Point):
    class Config:
        orm_mode = True

from datetime import date
from typing import Optional

import strawberry
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


class HTTPNotFoundError(BaseModel):
    detail: str


@strawberry.type(description="Postcode")
@dataclass
class Postcode:
    # pcd: str
    # pcd2: str
    pcds: str
    dointr: Optional[date] = None
    doterm: Optional[date] = None
    usertype: Optional[int] = None
    oseast1m: Optional[int] = None
    osnrth1m: Optional[int] = None
    osnrth1m: Optional[int] = None
    osgrdind: Optional[int] = None
    oa11: Optional[str] = Field(None, title="Output Area 2011 (GSS Code)")
    cty: Optional[str] = Field(None, title="County (GSS Code)")
    ced: Optional[str] = None
    laua: Optional[str] = Field(None, title="Local Authority (GSS Code)")
    ward: Optional[str] = Field(None, title="Ward (GSS Code)")
    hlthau: Optional[str] = Field(None, title="Health Authority (GSS Code)")
    nhser: Optional[str] = None
    ctry: Optional[str] = Field(None, title="Country (GSS Code)")
    rgn: Optional[str] = Field(None, title="Region (GSS Code)")
    pcon: Optional[str] = Field(None, title="Parliamentary Constituency (GSS Code)")
    eer: Optional[str] = None
    teclec: Optional[str] = None
    ttwa: Optional[str] = Field(None, title="Travel to Work Area (GSS Code)")
    pct: Optional[str] = Field(None, title="Primary Care Trust (GSS Code)")
    nuts: Optional[str] = None
    npark: Optional[str] = Field(None, title="National Park (GSS Code)")
    lsoa11: Optional[str] = Field(None, title="Lower Super Output Area (GSS Code)")
    msoa11: Optional[str] = Field(None, title="Middle Super Output Area (GSS Code)")
    wz11: Optional[str] = None
    ccg: Optional[str] = None
    bua11: Optional[str] = None
    buasd11: Optional[str] = None
    ru11ind: Optional[str] = None
    oac11: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    lep1: Optional[str] = None
    lep2: Optional[str] = None
    pfa: Optional[str] = None
    imd: Optional[int] = None
    calncv: Optional[str] = None
    stp: Optional[str] = None
    # hash: Optional[str] = None

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

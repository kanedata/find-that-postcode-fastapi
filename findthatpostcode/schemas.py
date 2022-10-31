from datetime import date
from typing import List, Optional

import strawberry
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from findthatpostcode import settings
from findthatpostcode.commands.placenames import PLACE_TYPES


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
    cty_name: Optional[str] = Field(None, title="County (Name)")
    ced: Optional[str] = None
    laua: Optional[str] = Field(None, title="Local Authority (GSS Code)")
    laua_name: Optional[str] = Field(None, title="Local Authority (Name)")
    ward: Optional[str] = Field(None, title="Ward (GSS Code)")
    ward_name: Optional[str] = Field(None, title="Ward (Name)")
    hlthau: Optional[str] = Field(None, title="Health Authority (GSS Code)")
    hlthau_name: Optional[str] = Field(None, title="Health Authority (Name)")
    nhser: Optional[str] = None
    ctry: Optional[str] = Field(None, title="Country (GSS Code)")
    ctry_name: Optional[str] = Field(None, title="Country (Name)")
    rgn: Optional[str] = Field(None, title="Region (GSS Code)")
    rgn_name: Optional[str] = Field(None, title="Region (Name)")
    pcon: Optional[str] = Field(None, title="Parliamentary Constituency (GSS Code)")
    pcon_name: Optional[str] = Field(None, title="Parliamentary Constituency (Name)")
    eer: Optional[str] = None
    teclec: Optional[str] = None
    ttwa: Optional[str] = Field(None, title="Travel to Work Area (GSS Code)")
    ttwa_name: Optional[str] = Field(None, title="Travel to Work Area (Name)")
    pct: Optional[str] = Field(None, title="Primary Care Trust (GSS Code)")
    pct_name: Optional[str] = Field(None, title="Primary Care Trust (Name)")
    nuts: Optional[str] = None
    npark: Optional[str] = Field(None, title="National Park (GSS Code)")
    npark_name: Optional[str] = Field(None, title="National Park (Name)")
    lsoa11: Optional[str] = Field(None, title="Lower Super Output Area (GSS Code)")
    lsoa11_name: Optional[str] = Field(None, title="Lower Super Output Area (Name)")
    msoa11: Optional[str] = Field(None, title="Middle Super Output Area (GSS Code)")
    msoa11_name: Optional[str] = Field(None, title="Middle Super Output Area (Name)")
    wz11: Optional[str] = None
    ccg: Optional[str] = Field(None, title="Clinical Commissioning Group (GSS Code)")
    ccg_name: Optional[str] = Field(None, title="Clinical Commissioning Group (Name)")
    bua11: Optional[str] = None
    buasd11: Optional[str] = None
    ru11ind: Optional[str] = None
    oac11: Optional[str] = None
    lat: Optional[float] = Field(None, title="Latitude")
    long: Optional[float] = Field(None, title="Longitude")
    lep1: Optional[str] = Field(None, title="Local Enterprise Partnership (GSS Code)")
    lep1_name: Optional[str] = Field(None, title="Local Enterprise Partnership (Name)")
    lep2: Optional[str] = Field(None, title="Local Enterprise Partnership 2 (GSS Code)")
    lep2_name: Optional[str] = Field(
        None, title="Local Enterprise Partnership 2 (Name)"
    )
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


@strawberry.type
@dataclass
class Area:
    code: str
    name: str
    name_welsh: Optional[str] = None
    areachect: Optional[float] = None
    areaehect: Optional[float] = None
    areaihect: Optional[float] = None
    arealhect: Optional[float] = None
    child_count: Optional[int] = None
    # child_counts: JSON = None
    date_end: Optional[date] = None
    date_start: Optional[date] = None
    entity: Optional[str] = None
    # equivalents: JSON() = None
    owner: Optional[str] = None
    parent: Optional[str] = None
    predecessor: Optional[List[str]] = None
    successor: Optional[List[str]] = None
    sort_order: Optional[str] = None
    statutory_instrument_id: Optional[str] = None
    statutory_instrument_title: Optional[str] = None
    has_boundary: Optional[bool] = None

    class Config:
        orm_mode = True

    def get_areatype(self) -> str:
        return settings.AREA_TYPES.get(settings.ENTITIES.get(self.entity))


@strawberry.type
@dataclass
class Placename:
    place18cd: str
    place18nm: str
    splitind: Optional[bool] = None
    descnm: Optional[str] = None
    ctyhistnam: Optional[str] = None
    ctyltnm: Optional[str] = None
    cty: Optional[str] = None
    laua: Optional[str] = None
    ward: Optional[str] = None
    parish: Optional[str] = None
    hlth: Optional[str] = None
    rgd: Optional[str] = None
    rgn: Optional[str] = None
    park: Optional[str] = None
    bua11: Optional[str] = None
    pcon: Optional[str] = None
    eer: Optional[str] = None
    pfa: Optional[str] = None
    cty: Optional[str] = None
    laua: Optional[str] = None
    ward: Optional[str] = None
    parish: Optional[str] = None
    hlth: Optional[str] = None
    rgd: Optional[str] = None
    rgn: Optional[str] = None
    park: Optional[str] = None
    bua11: Optional[str] = None
    pcon: Optional[str] = None
    eer: Optional[str] = None
    pfa: Optional[str] = None
    gridgb1m: Optional[str] = None
    gridgb1e: Optional[int] = None
    gridgb1n: Optional[int] = None
    grid1km: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    # location: Optional[Point] = None
    alternative_names: Optional[List[str]] = None

    @property
    def code(self) -> str:
        return self.place18cd

    @property
    def name(self) -> str:
        return self.place18nm

    def get_areatype(self) -> dict:
        description = PLACE_TYPES.get(self.descnm)
        if description:
            return {"name": "Place - {}".format(description[0])}
        return {"name": "Place"}

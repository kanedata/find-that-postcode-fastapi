from datetime import date
from typing import List, Literal, Optional

import strawberry
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from findthatpostcode import settings
from findthatpostcode.commands.placenames import PLACE_TYPES
from findthatpostcode.utils import PostcodeStr


class HTTPNotFoundError(BaseModel):
    detail: str


oac11_type = Literal["supergroup", "group", "subgroup"]


@strawberry.type(description="Lat Long")
@dataclass
class LatLng:
    lat: float
    lon: float


@strawberry.type(description="Postcode")
@dataclass
class Postcode:
    pcds: str
    pcd: Optional[str] = None
    pcd2: Optional[str] = None
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
    nhser: Optional[str] = Field(None, title="NHS England Region (GSS Code)")
    nhser_name: Optional[str] = Field(None, title="NHS England Region (Name)")
    ctry: Optional[str] = Field(None, title="Country (GSS Code)")
    ctry_name: Optional[str] = Field(None, title="Country (Name)")
    rgn: Optional[str] = Field(None, title="Region (GSS Code)")
    rgn_name: Optional[str] = Field(None, title="Region (Name)")
    pcon: Optional[str] = Field(None, title="Parliamentary Constituency (GSS Code)")
    pcon_name: Optional[str] = Field(None, title="Parliamentary Constituency (Name)")
    ttwa: Optional[str] = Field(None, title="Travel to Work Area (GSS Code)")
    ttwa_name: Optional[str] = Field(None, title="Travel to Work Area (Name)")
    nuts: Optional[str] = None
    npark: Optional[str] = Field(None, title="National Park (GSS Code)")
    npark_name: Optional[str] = Field(None, title="National Park (Name)")
    lsoa11: Optional[str] = Field(None, title="Lower Super Output Area (GSS Code)")
    lsoa11_name: Optional[str] = Field(None, title="Lower Super Output Area (Name)")
    msoa11: Optional[str] = Field(None, title="Middle Super Output Area (GSS Code)")
    msoa11_name: Optional[str] = Field(None, title="Middle Super Output Area (Name)")
    wz11: Optional[str] = Field(None, title="Workplace Zone (GSS Code)")
    wz11_name: Optional[str] = Field(None, title="Workplace Zone (Name)")
    ccg: Optional[str] = Field(None, title="Clinical Commissioning Group (GSS Code)")
    ccg_name: Optional[str] = Field(None, title="Clinical Commissioning Group (Name)")
    bua11: Optional[str] = Field(None, title="Built up Area (GSS Code)")
    bua11_name: Optional[str] = Field(None, title="Built up Area (Name)")
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
    pfa: Optional[str] = Field(None, title="Police Force Area (GSS Code)")
    pfa_name: Optional[str] = Field(None, title="Police Force Area (Name)")
    imd: Optional[int] = None
    stp: Optional[str] = None
    # hash: Optional[str] = None

    location: Optional[LatLng] = None

    class Config:
        orm_mode = True

    @property
    def pcd_outward(self) -> str:
        return PostcodeStr(self.pcds).postcode_district

    @property
    def pcd_inward(self) -> str:
        return PostcodeStr(self.pcds).inward

    @property
    def pcd_area(self) -> str:
        return PostcodeStr(self.pcds).postcode_area

    @property
    def pcd_district(self) -> str:
        # district is another name for outward code
        return self.pcd_outward

    @property
    def pcd_sector(self) -> str:
        return PostcodeStr(self.pcds).postcode_sector

    @property
    def id(self) -> str:
        return self.pcds

    def get_area(self, areatype) -> Optional["Area"]:
        area_code = getattr(self, areatype, None)
        if not isinstance(area_code, str):
            return None
        return Area(
            code=area_code,
            name=getattr(self, areatype + "_name", area_code),
            entity=area_code[0:3],
        )

    def get_oac11(self, oactype: oac11_type) -> Optional[str]:
        oac11 = self.oac11
        if not isinstance(oac11, str):
            return None
        type_index = ["supergroup", "group", "subgroup"].index(oactype)
        return settings.OAC11_CODE[oac11][type_index]

    def get_ru11ind_decsription(self) -> Optional[str]:
        ru11ind = self.ru11ind
        if not isinstance(ru11ind, str):
            return None
        return settings.RU11IND_CODES.get(ru11ind)


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
    name: Optional[str] = None
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
        descnm = self.descnm
        if descnm:
            description = PLACE_TYPES.get(descnm)
            if description:
                return {"name": "Place - {}".format(description[0])}
        return {"name": "Place"}


@dataclass
class AreaSearchResults:
    result_count: int
    result: List[Area | Placename | Postcode]
    scores: List[float]


@dataclass
class PostcodeHashResults:
    data: List[Postcode]

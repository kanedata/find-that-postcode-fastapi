import dataclasses
from typing import List, Tuple, Optional

from geoalchemy2.comparator import Comparator
from sqlalchemy import func
from sqlalchemy.orm import Session, defer, load_only

from findthatpostcode import models, schemas
from findthatpostcode.db import get_db
from findthatpostcode.documents import Postcode


area_names = {}


def get_fields(model, fields: List[str] = None) -> List[str]:
    all_fields = model.__table__.columns.keys()
    if not fields:
        return all_fields
    return [field for field in fields if field in all_fields]


def postcode_get_fields(
    fields: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    if fields:
        fields = set(fields)
        name_fields = [f for f in fields if f.endswith("_name")]
        fields.update([f.replace("_name", "") for f in name_fields])
        fields.add("pcds")
    else:
        name_fields = [
            f.name
            for f in dataclasses.fields(schemas.Postcode)
            if f.name.endswith("_name")
        ]
    return fields, name_fields


def record_to_schema(record, schema, name_fields=None, name_lookup=None, **kwargs):
    schema_keys = {field.name for field in dataclasses.fields(schema)}
    record = schema(
        **kwargs, **{k: v for k, v in record.__dict__.items() if k in schema_keys}
    )
    if name_fields and name_lookup:
        for f in name_fields:
            name = name_lookup.get(getattr(record, f.replace("_name", "")))
            if name:
                setattr(record, f, name[0])
    return record


def get_area_names(db: Session):
    if not area_names:
        records = (
            db.query(models.Area)
            .options(load_only("code", "name", "name_welsh"))
            .filter(models.Area.name != None)
            .all()
        )
        for area in records:
            area_names[area.code] = (area.name, area.name_welsh)
    return area_names


def get_postcode(
    db: Session, postcode: str, fields: List[str] = None
) -> schemas.Postcode:
    es = get_db()
    postcode = Postcode.parse_id(postcode)
    return Postcode.get(id=postcode, using=es)
    fields, name_fields = postcode_get_fields(fields)
    record = (
        db.query(models.Postcode)
        .options(load_only(*get_fields(models.Postcode, fields)))
        .filter(models.Postcode.pcds == postcode)
        .first()
    )
    if not record:
        return None
    name_lookup = get_area_names(db)
    record = record_to_schema(record, schemas.Postcode, name_fields, name_lookup)
    return record


def get_postcodes(
    db: Session, postcodes: str, fields: List[str] = None
) -> schemas.Postcode:
    postcodes = [models.Postcode.parse_id(postcode) for postcode in postcodes]
    fields, name_fields = postcode_get_fields(fields)
    records = (
        db.query(models.Postcode)
        .options(load_only(*get_fields(models.Postcode, fields)))
        .filter(models.Postcode.pcds.in_(postcodes))
        .all()
    )
    if not records:
        return None
    name_lookup = get_area_names(db)
    return [
        record_to_schema(record, schemas.Postcode, name_fields, name_lookup)
        for record in records
    ]


def get_nearest_postcode(
    db: Session, lat: float, long: float, fields: List[str] = None
) -> schemas.NearestPoint:
    fields, name_fields = postcode_get_fields(fields)
    record = (
        db.query(models.Postcode)
        .options(load_only(*get_fields(models.Postcode, fields)))
        .order_by(
            Comparator.distance_centroid(
                models.Postcode.geom,
                func.Geometry(
                    func.ST_GeographyFromText("POINT({} {})".format(long, lat))
                ),
            )
        )
        .limit(1)
        .first()
    )
    if not record:
        return None
    name_lookup = get_area_names(db)
    return record_to_schema(
        record,
        schemas.NearestPoint,
        name_fields,
        name_lookup,
        point_lat=lat,
        point_long=long,
    )


def get_postcode_by_hash(
    db: Session, hashes: List[str], fields: List[str] = None
) -> List[schemas.Postcode]:

    if not isinstance(hashes, list):
        hashes = [hashes]
    fields, name_fields = postcode_get_fields(fields)
    results = (
        db.query(models.Postcode)
        .options(load_only(*get_fields(models.Postcode, fields)))
        .filter(models.Postcode.hash4.in_(hashes))
        .all()
    )
    name_lookup = get_area_names(db)
    for result in results:
        yield record_to_schema(result, schemas.Postcode, name_fields, name_lookup)


def get_area(db: Session, areacode: str, fields: List[str] = None) -> schemas.Area:
    record = (
        db.query(models.Area)
        .options(load_only(*get_fields(models.Area, fields)))
        .filter(models.Area.code == areacode)
        .first()
    )
    if not record:
        return None
    return record_to_schema(record, schemas.Area, has_boundary=record.has_boundary)

import dataclasses
from typing import List

from geoalchemy2.comparator import Comparator
from sqlalchemy import func
from sqlalchemy.orm import Session, load_only, defer

from findthatpostcode import models, schemas


def get_fields(model, fields: List[str] = None) -> List[str]:
    all_fields = model.__table__.columns.keys()
    if not fields:
        return all_fields
    return [field for field in fields if field in all_fields]


def record_to_schema(record, schema, **kwargs):
    schema_keys = {field.name for field in dataclasses.fields(schema)}
    return schema(
        **kwargs, **{k: v for k, v in record.__dict__.items() if k in schema_keys}
    )
    

area_names = {}
def get_area_names(db: Session):
    if not area_names:
        records = (
            db.query(models.Area)
            .options(load_only("code", "name", "name_welsh"))
            .all()
        )
        for area in records:
            area_names[area.code] = (area.name, area.name_welsh)
    return area_names


def get_postcode(
    db: Session, postcode: str, fields: List[str] = None
) -> schemas.Postcode:
    postcode = models.Postcode.parse_id(postcode)
    record = (
        db.query(models.Postcode)
        .options(load_only(*get_fields(models.Postcode, fields)))
        .filter(models.Postcode.pcds == postcode)
        .first()
    )
    if not record:
        return None
    area_names = get_area_names(db)
    record = record_to_schema(record, schemas.Postcode)

    return record


def get_postcodes(
    db: Session, postcodes: str, fields: List[str] = None
) -> schemas.Postcode:
    postcodes = [models.Postcode.parse_id(postcode) for postcode in postcodes]
    records = (
        db.query(models.Postcode)
        .options(load_only(*get_fields(models.Postcode, fields)))
        .filter(models.Postcode.pcds.in_(postcodes))
        .all()
    )
    if not records:
        return None
    return [record_to_schema(record, schemas.Postcode) for record in records]


def get_nearest_postcode(
    db: Session, lat: float, long: float, fields: List[str] = None
) -> schemas.NearestPoint:
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
    return record_to_schema(
        record, schemas.NearestPoint, point_lat=lat, point_long=long
    )


def get_postcode_by_hash(
    db: Session, hashes: List[str], fields: List[str] = None
) -> List[schemas.Postcode]:

    if not isinstance(hashes, list):
        hashes = [hashes]

    for hash in hashes:
        results = (
            db.query(models.Postcode)
            .options(load_only(*get_fields(models.Postcode, fields)))
            .filter(models.Postcode.hash.like(f"{hash}%"))
            .all()
        )
        for result in results:
            yield record_to_schema(result, schemas.Postcode)


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

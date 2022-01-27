import dataclasses

from geoalchemy2.comparator import Comparator
from sqlalchemy import func
from sqlalchemy.orm import Session

from findthatpostcode import models, schemas


def record_to_schema(record, schema, **kwargs):
    schema_keys = {field.name for field in dataclasses.fields(schema)}
    return schema(
        **kwargs, **{k: v for k, v in record.__dict__.items() if k in schema_keys}
    )


def get_postcode(db: Session, postcode: str):
    postcode = models.Postcode.parse_id(postcode)
    record = db.query(models.Postcode).filter(models.Postcode.pcds == postcode).first()
    if not record:
        return None
    return record_to_schema(record, schemas.Postcode)


def get_postcodes(db: Session, postcodes: str):
    postcodes = [models.Postcode.parse_id(postcode) for postcode in postcodes]
    records = (
        db.query(models.Postcode).filter(models.Postcode.pcds.in_(postcodes)).all()
    )
    if not records:
        return None
    return [record_to_schema(record, schemas.Postcode) for record in records]


def get_nearest_postcode(db: Session, lat: float, long: float):
    record = (
        db.query(models.Postcode)
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

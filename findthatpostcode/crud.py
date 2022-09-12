import dataclasses
import logging
from typing import List, Tuple, Optional
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q

from geoalchemy2.comparator import Comparator

from findthatpostcode import schemas
from findthatpostcode.db import get_db
from findthatpostcode.documents import Postcode, Area, Entity, Placename


logger = logging.getLogger(__name__)


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
        fields = list(fields)
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
        **kwargs,
        **{k: v for k, v in record.__dict__["_d_"].items() if k in schema_keys}
    )
    if name_fields and name_lookup:
        for f in name_fields:
            name = name_lookup.get(getattr(record, f.replace("_name", "")))
            if name:
                setattr(record, f, name[0])
    return record


def get_area_names(db: Elasticsearch, area_codes: List = []) -> dict:
    search = Area.mget(area_codes, using=db, missing="skip")
    return {
        area.code: (area.name, area.type)
        for area in search
        if area and (area.name or area.name_welsh)
    }


def get_postcode(
    db: Elasticsearch, postcode: str, fields: List[str] = None
) -> schemas.Postcode:
    postcode = Postcode.parse_id(postcode)
    fields, name_fields = postcode_get_fields(fields)
    record = Postcode.get(id=postcode, using=db, _source_includes=fields)
    if not record:
        return None
    name_lookup = get_area_names(db, record.area_codes())
    record = record_to_schema(record, schemas.Postcode, name_fields, name_lookup)
    return record


def get_postcodes(
    db: Elasticsearch, postcodes: str, fields: List[str] = None
) -> schemas.Postcode:
    cleaned_postcodes = {
        postcode: Postcode.parse_id(postcode) for postcode in postcodes
    }
    fields, name_fields = postcode_get_fields(fields)
    records = {
        p.pcds: p
        for p in Postcode.mget(
            cleaned_postcodes.values(),
            using=db,
            _source_includes=fields,
            missing="skip",
        )
    }
    return [
        record_to_schema(
            records[cleaned_postcode],
            schemas.Postcode,
            name_fields,
            get_area_names(db, records[cleaned_postcode].area_codes()),
        )
        if records.get(cleaned_postcode)
        else schemas.Postcode(pcds=postcode)
        for postcode, cleaned_postcode in cleaned_postcodes.items()
    ]


def get_nearest_postcode(
    db: Elasticsearch, lat: float, long: float, fields: List[str] = None
) -> schemas.NearestPoint:
    return None
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
    db: Elasticsearch, hashes: List[str], fields: List[str] = None
) -> List[schemas.Postcode]:
    return None
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


def get_area(
    db: Elasticsearch, areacode: str, fields: List[str] = None
) -> schemas.Area:
    return None
    record = (
        db.query(models.Area)
        .options(load_only(*get_fields(models.Area, fields)))
        .filter(models.Area.code == areacode)
        .first()
    )
    if not record:
        return None
    return record_to_schema(record, schemas.Area, has_boundary=record.has_boundary)

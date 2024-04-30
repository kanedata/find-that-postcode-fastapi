import dataclasses
import io
import json
import logging
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    overload,
)

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from mypy_boto3_s3.client import S3Client
from pydantic_geojson import FeatureModel

from findthatpostcode import schemas, settings
from findthatpostcode.documents import Area, Placename, Postcode
from findthatpostcode.utils import PostcodeStr

logger = logging.getLogger(__name__)


def get_fields(model, fields: Optional[List[str]] = None) -> List[str]:
    all_fields = model.__table__.columns.keys()
    if not fields:
        return all_fields
    return [field for field in fields if field in all_fields]


def postcode_get_fields(
    fields: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    if fields is None:
        fields = []
    if fields:
        fields_set = set(fields)
        name_fields = [f for f in fields_set if f.endswith("_name")]
        fields_set.update([f.replace("_name", "") for f in name_fields])
        fields_set.add("pcds")
        fields = list(fields_set)
    else:
        name_fields = [
            f.name
            for f in dataclasses.fields(schemas.Postcode)
            if f.name.endswith("_name")
        ]
    return fields, name_fields


@overload
def record_to_schema(
    record: Area,
    schema: Type[schemas.Area],
    name_fields: Optional[List[str]] = None,
    name_lookup: Optional[Dict[str, Optional[str]]] = None,
    **kwargs,
) -> schemas.Area: ...


@overload
def record_to_schema(
    record: Placename,
    schema: Type[schemas.Placename],
    name_fields: Optional[List[str]] = None,
    name_lookup: Optional[Dict[str, Optional[str]]] = None,
    **kwargs,
) -> schemas.Placename: ...


@overload
def record_to_schema(
    record: Postcode,
    schema: Type[schemas.NearestPoint],
    name_fields: Optional[List[str]] = None,
    name_lookup: Optional[Dict[str, Optional[str]]] = None,
    **kwargs,
) -> schemas.NearestPoint: ...


@overload
def record_to_schema(
    record: Postcode,
    schema: Type[schemas.Postcode],
    name_fields: Optional[List[str]] = None,
    name_lookup: Optional[Dict[str, Optional[str]]] = None,
    **kwargs,
) -> schemas.Postcode: ...


def record_to_schema(
    record,
    schema,
    name_fields: Optional[List[str]] = None,
    name_lookup: Optional[Dict[str, Optional[str]]] = None,
    **kwargs,
):
    schema_keys = {field.name for field in dataclasses.fields(schema)}
    record_values = dict(
        **kwargs,
        **{k: v for k, v in record.__dict__["_d_"].items() if k in schema_keys},
    )
    new_record = schema(**record_values)
    if name_fields and name_lookup:
        for f in name_fields:
            name = name_lookup.get(getattr(new_record, f.replace("_name", "")))
            if name:
                setattr(new_record, f, name[0])
    return new_record


def get_area_names(db: Elasticsearch, area_codes: List = []) -> dict:
    search = Area.mget(area_codes, using=db, missing="skip")
    return {
        area.code: (area.name, area.type)
        for area in search
        if area and (area.name or area.name_welsh)
    }


def get_postcode(
    db: Elasticsearch, postcode: str, fields: Optional[List[str]] = None
) -> Optional[schemas.Postcode]:
    try:
        postcode_parsed = PostcodeStr(postcode)
    except ValueError:
        return None
    fields, name_fields = postcode_get_fields(fields)
    record = Postcode.get(id=postcode_parsed, using=db, _source_includes=fields)
    if not record:
        return None
    name_lookup = get_area_names(db, record.area_codes())
    record = record_to_schema(record, schemas.Postcode, name_fields, name_lookup)
    return record


def get_postcodes(
    db: Elasticsearch, postcodes: List[str], fields: Optional[List[str]] = None
) -> List[schemas.Postcode]:
    cleaned_postcodes: Dict[str, Any] = {}
    for postcode in postcodes:
        try:
            cleaned_postcodes[postcode] = PostcodeStr(postcode)
        except ValueError:
            cleaned_postcodes[postcode] = postcode
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
    db: Elasticsearch, lat: float, long: float, fields: Optional[List[str]] = None
) -> Optional[schemas.NearestPoint]:
    fields, name_fields = postcode_get_fields(fields)
    results = (
        Postcode.search(using=db)
        .query(Q("bool", must_not=Q("exists", field="doterm")))
        .sort({"_geo_distance": dict(location={"lat": lat, "lon": long}, unit="m")})[
            0:1
        ]
        .execute()
    )
    if not results.hits:
        return None
    record: Postcode = results.hits[0]
    if not record:
        return None
    name_lookup = get_area_names(db, record.area_codes())
    return record_to_schema(
        record,
        schemas.NearestPoint,
        name_fields,
        name_lookup,
        point_lat=lat,
        point_long=long,
    )


def get_postcode_by_hash(
    db: Elasticsearch, hashes: List[str], fields: Optional[List[str]] = None
) -> Generator[schemas.Postcode, None, None]:
    if not isinstance(hashes, list):
        hashes = [hashes]
    fields, name_fields = postcode_get_fields(fields)
    query = []
    for hash_ in hashes:
        if len(hash_) < 3:
            raise ValueError("Hash length must be at least 3 characters")
        query.append(
            {
                "prefix": {
                    "hash": hash_,
                },
            }
        )

    results = (
        Postcode.search(using=db)
        .source(include=fields + name_fields)
        .query("bool", should=query)
        .execute()
    )
    name_lookup = {}
    for result in results:
        area_codes_to_check = set()
        for code in result.area_codes():
            if code not in name_lookup:
                area_codes_to_check.add(code)
        if area_codes_to_check:
            name_lookup = {
                **name_lookup,
                **get_area_names(db, list(area_codes_to_check)),
            }
        yield record_to_schema(result, schemas.Postcode, name_fields, name_lookup)


def get_area(
    db: Elasticsearch, areacode: str, fields: Optional[List[str]] = None
) -> Optional[schemas.Area]:
    record = Area.get(
        id=areacode, using=db, _source_includes=fields, _source_excludes=["boundary"]
    )
    if not record:
        return None
    return record_to_schema(record, schemas.Area)


def get_area_boundary(
    db: Elasticsearch, client: S3Client, areacode: str
) -> Optional[FeatureModel]:
    record = Area.exists(id=areacode, using=db)
    if not record:
        return None

    buffer = io.BytesIO()
    prefix = areacode[0:3]
    client.download_fileobj(
        settings.S3_BUCKET,
        "%s/%s.json" % (prefix, areacode),
        buffer,
    )
    boundary = json.loads(buffer.getvalue().decode("utf-8"))
    return boundary


def search_areas(
    db: Elasticsearch, q: str, pagination=None
) -> schemas.AreaSearchResults:
    """
    Search for areas based on a name
    """
    query = {
        "query": {
            "function_score": {
                "query": {"query_string": {"query": q}},
                "boost": "5",
                "functions": [
                    {"weight": 0.1, "filter": {"term": {"active": False}}},
                    {"weight": 6, "filter": {"exists": {"field": "type"}}},
                    {
                        "weight": 3,
                        "filter": {
                            "terms": {
                                "type": ["ctry", "region", "cty", "laua", "rgn", "LOC"]
                            }
                        },
                    },
                    {
                        "weight": 2,
                        "filter": {
                            "terms": {"type": ["ttwa", "pfa", "lep", "park", "pcon"]}
                        },
                    },
                    {
                        "weight": 1.5,
                        "filter": {"terms": {"type": ["ccg", "hlthau", "hro", "pct"]}},
                    },
                    {
                        "weight": 1,
                        "filter": {
                            "terms": {"type": ["eer", "bua11", "buasd11", "teclec"]}
                        },
                    },
                    {
                        "weight": 0.4,
                        "filter": {
                            "terms": {
                                "type": [
                                    "msoa11",
                                    "lsoa11",
                                    "wz11",
                                    "oa11",
                                    "nuts",
                                    "ward",
                                ]
                            }
                        },
                    },
                ],
            }
        }
    }
    if pagination:
        result = db.search(
            index="geo_area,geo_placename",
            body=query,
            from_=pagination.from_,  # type: ignore
            size=pagination.size,  # type: ignore
            _source_excludes=["boundary"],  # type: ignore
            ignore=[404],  # type: ignore
        )
    else:
        result = db.search(
            index="geo_area,geo_placename",
            body=query,
            _source_excludes=["boundary"],  # type: ignore
            ignore=[404],  # type: ignore
        )
    return_result = []
    for a in result.get("hits", {}).get("hits", []):
        if a["_index"] == "geo_placename":
            return_result.append(
                record_to_schema(Placename(**a["_source"]), schemas.Placename)
            )
        else:
            if a["_source"].get("date_start"):
                a["_source"]["date_start"] = a["_source"]["date_start"][0:10]
            return_result.append(record_to_schema(Area(**a["_source"]), schemas.Area))
    total = result.get("hits", {}).get("total", 0)
    if isinstance(total, dict):
        total = total.get("value", 0)
    return schemas.AreaSearchResults(
        result=return_result,
        scores=[a["_score"] for a in result.get("hits", {}).get("hits", [])],
        result_count=total,
    )

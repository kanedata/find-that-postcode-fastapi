from typing import List, Optional

import strawberry
from graphql.pyutils import camel_to_snake
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from findthatpostcode import crud, schemas
from findthatpostcode.database import get_db


def get_selected_fields(info):
    for s in info.selected_fields[0].selections:
        yield camel_to_snake(s.name)


@strawberry.type
class Query:
    @strawberry.field
    def get_postcode(self, postcode: str, info: Info) -> Optional[schemas.Postcode]:
        db = get_db()
        for conn in db:
            return crud.get_postcode(conn, postcode, fields=get_selected_fields(info))

    @strawberry.field
    def get_postcodes(
        self, postcodes: List[str], info: Info
    ) -> Optional[List[schemas.Postcode]]:

        db = get_db()
        for conn in db:
            return crud.get_postcodes(conn, postcodes, fields=get_selected_fields(info))

    @strawberry.field
    def get_nearest_point(
        self, lat: float, long: float, info: Info
    ) -> Optional[schemas.NearestPoint]:

        db = get_db()
        for conn in db:
            return crud.get_nearest_postcode(
                conn, lat, long, fields=get_selected_fields(info)
            )


schema = strawberry.Schema(Query)

router = GraphQLRouter(schema)

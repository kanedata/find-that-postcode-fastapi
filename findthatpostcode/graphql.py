from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

from findthatpostcode import crud, schemas
from findthatpostcode.database import get_db


@strawberry.type
class Query:
    @strawberry.field
    def get_postcode(self, postcode: str) -> Optional[schemas.Postcode]:

        db = get_db()
        for conn in db:
            return crud.get_postcode(conn, postcode)

    @strawberry.field
    def get_postcodes(self, postcodes: List[str]) -> Optional[List[schemas.Postcode]]:

        db = get_db()
        for conn in db:
            return crud.get_postcodes(conn, postcodes)

    @strawberry.field
    def get_nearest_point(
        self, lat: float, long: float
    ) -> Optional[schemas.NearestPoint]:

        db = get_db()
        for conn in db:
            return crud.get_nearest_postcode(conn, lat, long)


schema = strawberry.Schema(Query)

router = GraphQLRouter(schema)

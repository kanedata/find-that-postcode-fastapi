from typing import Optional, List
import strawberry
from strawberry.fastapi import GraphQLRouter

from findthatpostcode.schemas import Postcode
from findthatpostcode import models
from findthatpostcode.database import get_db

@strawberry.type
class Query:

    @strawberry.field
    def get_postcode(self, postcode: str) -> Optional[Postcode]:
        
        db = get_db()
        for conn in db:
            postcode_item = (
                conn.query(models.Postcode)
                .filter(models.Postcode.pcds == models.Postcode.parse_id(postcode))
                .first()
            )
            if not postcode_item:
                return None
            return postcode_item

    @strawberry.field
    def get_postcodes(self, postcodes: List[str]) -> Optional[List[Postcode]]:

        postcodes = [models.Postcode.parse_id(postcode) for postcode in postcodes]
        
        db = get_db()
        for conn in db:
            postcode_items = (
                conn.query(models.Postcode)
                .filter(models.Postcode.pcds.in_(postcodes))
                .all()
            )
            if not postcode_items:
                return None
            return postcode_items

schema = strawberry.Schema(Query)

router = GraphQLRouter(schema)

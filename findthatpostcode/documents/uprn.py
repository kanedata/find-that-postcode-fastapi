from elasticsearch_dsl import (
    Document,
    Keyword,
)


class UPRN(Document):
    uprn = Keyword()

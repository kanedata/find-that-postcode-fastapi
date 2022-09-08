from elasticsearch_dsl import (
    Document,
    Date,
    Nested,
    Boolean,
    analyzer,
    InnerDoc,
    Completion,
    Keyword,
    Text,
)


class UPRN(Document):
    uprn = Keyword()

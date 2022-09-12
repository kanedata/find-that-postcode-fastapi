from elasticsearch_dsl import (
    Boolean,
    Completion,
    Date,
    Document,
    InnerDoc,
    Keyword,
    Nested,
    Text,
    analyzer,
)


class UPRN(Document):
    uprn = Keyword()

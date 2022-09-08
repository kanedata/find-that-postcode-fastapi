import click
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Index
from findthatpostcode import settings, documents


def get_db(**kwargs):
    return Elasticsearch(settings.ES_URL, timeout=120, **kwargs)


def close_db(e=None):
    pass


def init_db(reset=False):
    es = get_db()
    for doc_type in documents.__all__:
        DocumentType = getattr(documents, doc_type)
        DocumentIndex = Index(DocumentType.Index.name)
        if reset:
            click.echo(f"[elasticsearch] deleting '{DocumentType.Index.name}' index...")
            res = DocumentIndex.delete(using=es, ignore=[400, 404])
            click.echo(f"[elasticsearch] response: '{res}'")
        click.echo(f"[elasticsearch] creating '{DocumentType.Index.name}' index...")
        DocumentIndex.create(using=es)

import click
from boto3 import session
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Index

from findthatpostcode import documents, settings


def get_db():
    return Elasticsearch(settings.ES_URL, timeout=120)


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


def get_s3_client():
    s3_session = session.Session()
    return s3_session.client(
        "s3",
        region_name=settings.S3_REGION,
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_ID,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )


def close_s3_client(e=None):
    pass

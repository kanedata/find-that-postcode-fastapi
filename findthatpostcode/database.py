from sqlalchemy import Boolean, Column, DateTime, create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from findthatpostcode.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upsert_statement(model, index_elements):
    insert_stmt = postgresql.insert(model.__table__)
    update_columns = {
        col.name: col for col in insert_stmt.excluded if col.name not in ("id",)
    }
    return insert_stmt.on_conflict_do_update(
        index_elements=index_elements, set_=update_columns
    )


class UpdatingTable:
    active = Column(Boolean(), default=True)
    updated = Column(DateTime())

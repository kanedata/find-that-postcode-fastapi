from logging.config import fileConfig

from alembic import context
from geoalchemy2 import Geography, Geometry, Raster, _check_spatial_type
from sqlalchemy import engine_from_config, pool

from findthatpostcode import settings

config = context.config
fileConfig(config.config_file_name)

from findthatpostcode.models import Base

target_metadata = Base.metadata


def exclude_tables_from_config(config_):
    if not config_:
        return []
    tables_ = config_.get("tables", "")
    return [t.strip() for t in tables_.split(",")]


exclude_tables = exclude_tables_from_config(config.get_section("alembic:exclude"))


def include_object(object, name, type_, *args, **kwargs):
    # exclude spatial indexes from being created
    # from: https://github.com/geoalchemy/geoalchemy2/issues/137#issuecomment-1022912227
    if type_ == "index":
        if len(object.expressions) == 1:
            try:
                col = object.expressions[0]
                if (
                    _check_spatial_type(col.type, (Geometry, Geography, Raster), None)
                    and col.type.spatial_index
                ):
                    return False
            except AttributeError:
                pass

    if type_ == "table" and name in exclude_tables:
        return False
    return True


def get_url():
    return settings.DATABASE_URL


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

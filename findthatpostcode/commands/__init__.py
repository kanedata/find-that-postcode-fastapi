import click

from . import postcodes, codes, boundaries, placenames, stats
from findthatpostcode.db import init_db


@click.command("init-db")
@click.option("--reset/--no-reset", default=False)
def init_db_command(reset):
    """Clear the existing data and create new tables."""
    init_db(reset)
    click.echo("Initialized the database.")


@click.group()
def cli():
    pass


@cli.group(name="import")
def import_group():
    pass


import_group.add_command(postcodes.import_nspl)
import_group.add_command(codes.import_rgc)
import_group.add_command(codes.import_chd)
import_group.add_command(codes.import_msoa_names)
import_group.add_command(boundaries.import_boundaries)
import_group.add_command(placenames.import_placenames)
import_group.add_command(stats.import_imd2015)
import_group.add_command(stats.import_imd2019)

cli.add_command(init_db_command)

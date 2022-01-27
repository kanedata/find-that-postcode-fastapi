import typer

import findthatpostcode.commands.codes
import findthatpostcode.commands.postcodes
from findthatpostcode.commands.import_app import app as import_app

app = typer.Typer()
app.add_typer(import_app, name="import")

import random
import zipfile

import click


@click.command("sample-zip")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def sample_zip(input, output):
    input_zip = zipfile.ZipFile(input)
    output_zip = zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED)

    for f in input_zip.filelist:
        # if the file is not a CSV then just copy it across
        if not f.filename.endswith(".csv"):
            output_zip.writestr(f, input_zip.read(f))
            continue

        # if it's a CSV the read it in and write out a sample
        with input_zip.open(f, "r") as pccsv:
            lines = pccsv.readlines()
            if len(lines) <= 1000:
                output_lines = lines
            else:
                output_lines = [lines[0]] + random.sample(lines[1:], 100)
            output_zip.writestr(f, b"".join(output_lines))
